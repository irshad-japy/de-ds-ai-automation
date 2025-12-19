from __future__ import annotations

import hashlib
import inspect
import json
import os
import shutil
import tempfile
from dataclasses import is_dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

def _safe_stat_signature(p: Path) -> dict[str, Any]:
    """
    Make file paths hashable without reading the whole file:
    include absolute path + size + mtime. (Good balance of speed vs correctness)
    """
    try:
        st = p.stat()
        return {
            "_type": "file",
            "path": str(p.resolve()),
            "size": st.st_size,
            "mtime": int(st.st_mtime),
        }
    except FileNotFoundError:
        return {"_type": "file", "path": str(p), "missing": True}

def _freeze(obj: Any) -> Any:
    """
    Convert args/kwargs into a JSON-serializable structure (stable for hashing).
    Handles common types used in pipelines: Path, datetime/date, bytes, dataclasses, lists/dicts/tuples.
    """
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    if isinstance(obj, Path):
        # If the Path is an input file, incorporate size/mtime to invalidate cache when it changes.
        return _safe_stat_signature(obj)

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, bytes):
        # Don’t hash huge bytes fully; hash the bytes and store the digest.
        return {"_type": "bytes", "sha1": hashlib.sha1(obj).hexdigest(), "len": len(obj)}

    if is_dataclass(obj):
        return {"_type": "dataclass", "data": _freeze(asdict(obj))}

    if isinstance(obj, dict):
        # Sort keys to keep stable
        return {str(k): _freeze(v) for k, v in sorted(obj.items(), key=lambda x: str(x[0]))}

    if isinstance(obj, (list, tuple, set)):
        return [_freeze(x) for x in obj]

    # Fallback: stable-ish string
    return {"_type": type(obj).__name__, "repr": repr(obj)}

def _hash_from_call(func_name: str, arg_map: dict[str, Any]) -> str:
    payload = {"function_name": func_name, "args": _freeze(arg_map)}
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def cache_file(
    cache_root: str | Path,
    *,
    enabled: bool = True,
    namespace: Optional[str] = None,
    out_arg: str = "out_path",
    ext: Optional[str] = None,
    ignore_args: Iterable[str] = ("self", "con", "conn", "client", "cursor", "session"),
    require_non_empty: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Path]]:
    """
    Cache ANY generated file (png/jpg/mp3/wav/mp4/etc) based on a hash of function call args.

    Supports:
      A) function has an output parameter (default: out_path) and writes the file there
      B) function returns:
          - a Path/str (path to a generated file), OR
          - bytes (raw file content)

    Returns:
      Wrapper returns the cached file Path.

    Concurrency safety:
      writes to temp file then atomic rename into final cache path.
    """
    cache_root = Path(cache_root)

    def decorator(func: Callable[..., Any]) -> Callable[..., Path]:
        sig = inspect.signature(func)

        def wrapper(*args: Any, **kwargs: Any) -> Path:
            if not enabled:
                # No caching -> just run and return whatever as Path best-effort
                result = func(*args, **kwargs)
                return Path(result) if result is not None else Path(kwargs[out_arg])

            # Bind args/kwargs to names (like your existing decorator style) :contentReference[oaicite:1]{index=1}
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            arg_map = dict(bound.arguments)
            for k in list(ignore_args):
                arg_map.pop(k, None)

            call_hash = _hash_from_call(func.__name__, arg_map)

            # Decide extension:
            # 1) explicit ext parameter
            # 2) if caller gave out_path with suffix -> reuse it
            # 3) else leave empty (you can enforce ext in your usage)
            chosen_ext = ext
            if not chosen_ext:
                out_val = arg_map.get(out_arg) or kwargs.get(out_arg)
                if out_val:
                    chosen_ext = Path(str(out_val)).suffix or ""
                else:
                    chosen_ext = ""

            if chosen_ext and not chosen_ext.startswith("."):
                chosen_ext = "." + chosen_ext

            subdir = cache_root / namespace if namespace else cache_root
            subdir.mkdir(parents=True, exist_ok=True)

            cache_path = subdir / f"{func.__name__}_{call_hash}{chosen_ext}"

            # Cache hit
            if cache_path.exists():
                if (not require_non_empty) or cache_path.stat().st_size > 0:
                    return cache_path

            # Cache miss: create temp file path in same directory for atomic rename
            tmp_fd, tmp_name = tempfile.mkstemp(prefix=cache_path.stem + "_", suffix=cache_path.suffix, dir=str(subdir))
            os.close(tmp_fd)
            tmp_path = Path(tmp_name)

            try:
                # If func accepts out_arg, force it to write into tmp_path
                if out_arg in sig.parameters:
                    kwargs2 = dict(kwargs)
                    kwargs2[out_arg] = str(tmp_path)
                    result = func(*args, **kwargs2)

                    # If function ignores out_path and returns something else, handle it
                    if isinstance(result, (str, Path)) and Path(str(result)).exists() and Path(str(result)) != tmp_path:
                        shutil.copy2(Path(str(result)), tmp_path)
                    elif isinstance(result, (bytes, bytearray)):
                        tmp_path.write_bytes(bytes(result))

                else:
                    # No out_arg support -> function must return bytes or a file path
                    result = func(*args, **kwargs)
                    if isinstance(result, (bytes, bytearray)):
                        tmp_path.write_bytes(bytes(result))
                    elif isinstance(result, (str, Path)):
                        src = Path(str(result))
                        if not src.exists():
                            raise FileNotFoundError(f"Function returned path but file not found: {src}")
                        shutil.copy2(src, tmp_path)
                    else:
                        raise TypeError(
                            f"{func.__name__} must accept '{out_arg}' or return bytes/Path/str for caching."
                        )

                # Validate temp output
                if require_non_empty and (not tmp_path.exists() or tmp_path.stat().st_size == 0):
                    raise RuntimeError(f"Generated cache file is empty: {tmp_path}")

                # Atomic replace into cache
                os.replace(str(tmp_path), str(cache_path))
                return cache_path

            finally:
                # Cleanup temp if still there (e.g., exception before rename)
                if tmp_path.exists() and tmp_path != cache_path:
                    try:
                        tmp_path.unlink()
                    except OSError:
                        pass

        return wrapper

    return decorator

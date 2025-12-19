from __future__ import annotations

import json
import os
import sys
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict

class SubprocessError(RuntimeError):
    pass

def run_worker(module: str, payload: Dict[str, Any]) -> str:
    """
    Run a worker module as: python -m <module> <payload_json_file>
    Worker must print the output path to stdout.
    """
    tmp_path = None
    try:
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(payload, f)
            tmp_path = f.name

        # Important: use the same python interpreter that runs uvicorn (poetry venv)
        cmd = [sys.executable, "-m", module, tmp_path]

        p = subprocess.run(cmd, capture_output=True, text=True)

        if p.returncode != 0:
            raise SubprocessError(
                f"Worker failed (code={p.returncode}).\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"
            )

        out = (p.stdout or "").strip()
        if not out:
            raise SubprocessError("Worker returned empty output path.")

        return out

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

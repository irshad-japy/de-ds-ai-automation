from __future__ import annotations

import asyncio
import functools
import inspect
import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable, Optional, Dict
from app.utils.structured_logging import log_message
import psutil

try:
    import pynvml  # pip install nvidia-ml-py3
    _NVML_AVAILABLE = True
except Exception:
    pynvml = None
    _NVML_AVAILABLE = False

@dataclass
class ProcMetrics:
    rss_bytes: int
    vms_bytes: int
    threads: int

@dataclass
class SysMetrics:
    cpu_percent: float
    mem_percent: float
    mem_used_bytes: int
    mem_total_bytes: int

@dataclass
class GpuMetrics:
    name: str
    gpu_util_percent: float
    mem_util_percent: float
    mem_used_bytes: int
    mem_total_bytes: int
    temperature_c: Optional[int] = None

def _structured_log(logger: logging.Logger, level: int, payload: Dict[str, Any]) -> None:
    level_name = logging.getLevelName(level)  # INFO / ERROR etc.
    logger.log(level, log_message(
        log_level=level_name,
        log_message="resource_monitor",
        log_context=payload
    ))

def _get_process() -> psutil.Process:
    return psutil.Process(os.getpid())

def get_proc_metrics(proc: psutil.Process) -> ProcMetrics:
    mem = proc.memory_info()
    return ProcMetrics(
        rss_bytes=int(mem.rss),
        vms_bytes=int(mem.vms),
        threads=int(proc.num_threads()),
    )

def get_sys_metrics() -> SysMetrics:
    vm = psutil.virtual_memory()
    # Note: cpu_percent() first call can be 0.0; consider "priming" at startup.
    cpu = float(psutil.cpu_percent(interval=None))
    return SysMetrics(
        cpu_percent=cpu,
        mem_percent=float(vm.percent),
        mem_used_bytes=int(vm.used),
        mem_total_bytes=int(vm.total),
    )

def _init_nvml_once() -> bool:
    if not _NVML_AVAILABLE:
        return False
    try:
        pynvml.nvmlInit()
        return True
    except Exception:
        return False

_NVML_OK = _init_nvml_once()

def get_gpu_metrics() -> Optional[GpuMetrics]:
    """Returns first GPU metrics if available, else None."""
    if not _NVML_OK:
        return None
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        name = pynvml.nvmlDeviceGetName(handle).decode("utf-8", errors="ignore")
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)

        temp = None
        try:
            temp = int(pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU))
        except Exception:
            pass

        mem_util = (mem.used / mem.total * 100.0) if mem.total else 0.0
        return GpuMetrics(
            name=name,
            gpu_util_percent=float(util.gpu),
            mem_util_percent=float(mem_util),
            mem_used_bytes=int(mem.used),
            mem_total_bytes=int(mem.total),
            temperature_c=temp,
        )
    except Exception:
        return None

def _find_request_context(args: tuple, kwargs: dict) -> Dict[str, Any]:
    """
    Best-effort extraction if FastAPI Request is passed as an argument.
    """
    ctx: Dict[str, Any] = {}
    req = kwargs.get("request", None)
    if req is None:
        for a in args:
            # Avoid importing fastapi/starlette types here; duck-type instead.
            if hasattr(a, "url") and hasattr(a, "method"):
                req = a
                break

    if req is not None:
        try:
            ctx["method"] = getattr(req, "method", None)
            ctx["path"] = getattr(getattr(req, "url", None), "path", None)
            client = getattr(req, "client", None)
            ctx["client_ip"] = getattr(client, "host", None) if client else None
        except Exception:
            pass
    return ctx


def resource_monitor(
    logger: logging.Logger,
    *,
    include_gpu: bool = True,
    slow_ms_threshold: int = 0,   # log only if request takes >= this many ms (0 = always)
    sample_rate: int = 1,         # log 1 out of N calls (1 = log all)
    tag: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to log resource usage around an endpoint call.
    Works for both sync and async functions.
    """

    counter = {"n": 0}

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await _run(func, args, kwargs, is_async=True)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return asyncio.run(_run(func, args, kwargs, is_async=False)) if False else _run_sync(func, args, kwargs)

        async def _run(fn: Callable[..., Any], args: tuple, kwargs: dict, *, is_async: bool) -> Any:
            # sampling
            counter["n"] += 1
            if sample_rate > 1 and (counter["n"] % sample_rate != 0):
                return await fn(*args, **kwargs)

            proc = _get_process()
            start_ts = time.perf_counter()
            start_cpu_times = proc.cpu_times()
            start_proc = get_proc_metrics(proc)
            start_sys = get_sys_metrics()
            start_gpu = get_gpu_metrics() if include_gpu else None

            status = "ok"
            result: Any = None
            try:
                result = await fn(*args, **kwargs)
                return result
            except Exception:
                status = "error"
                raise
            finally:
                end_ts = time.perf_counter()
                duration_s = max(end_ts - start_ts, 1e-9)
                duration_ms = int(duration_s * 1000)

                if slow_ms_threshold and duration_ms < slow_ms_threshold:
                    return  # skip logging for fast calls

                end_cpu_times = proc.cpu_times()
                end_proc = get_proc_metrics(proc)
                end_sys = get_sys_metrics()
                end_gpu = get_gpu_metrics() if include_gpu else None

                # Process CPU% over the request window:
                # (user+system seconds) / wall time / cpu_count * 100
                cpu_delta = (end_cpu_times.user + end_cpu_times.system) - (start_cpu_times.user + start_cpu_times.system)
                cpu_count = psutil.cpu_count() or 1
                proc_cpu_percent = float((cpu_delta / duration_s) * 100.0 / cpu_count)

                payload: Dict[str, Any] = {
                    "event": "resource_monitor",
                    "tag": tag,
                    "function": fn.__name__,
                    "status": status,
                    "latency_ms": duration_ms,
                    **_find_request_context(args, kwargs),
                    "proc": {
                        "cpu_percent_window": round(proc_cpu_percent, 2),
                        "rss_mb_start": round(start_proc.rss_bytes / (1024**2), 2),
                        "rss_mb_end": round(end_proc.rss_bytes / (1024**2), 2),
                        "rss_mb_delta": round((end_proc.rss_bytes - start_proc.rss_bytes) / (1024**2), 2),
                        "threads": end_proc.threads,
                    },
                    "sys": {
                        "cpu_percent_now": round(end_sys.cpu_percent, 2),
                        "mem_percent": round(end_sys.mem_percent, 2),
                        "mem_used_gb": round(end_sys.mem_used_bytes / (1024**3), 3),
                        "mem_total_gb": round(end_sys.mem_total_bytes / (1024**3), 3),
                    },
                }

                if include_gpu:
                    payload["gpu_start"] = asdict(start_gpu) if start_gpu else None
                    payload["gpu_end"] = asdict(end_gpu) if end_gpu else None

                _structured_log(logger, logging.INFO if status == "ok" else logging.ERROR, payload)

        def _run_sync(fn: Callable[..., Any], args: tuple, kwargs: dict) -> Any:
            # Run the same logic without awaiting
            # (Duplicated minimal to keep it simple & predictable)
            counter["n"] += 1
            if sample_rate > 1 and (counter["n"] % sample_rate != 0):
                return fn(*args, **kwargs)

            proc = _get_process()
            start_ts = time.perf_counter()
            start_cpu_times = proc.cpu_times()
            start_proc = get_proc_metrics(proc)
            start_gpu = get_gpu_metrics() if include_gpu else None

            status = "ok"
            try:
                return fn(*args, **kwargs)
            except Exception:
                status = "error"
                raise
            finally:
                end_ts = time.perf_counter()
                duration_s = max(end_ts - start_ts, 1e-9)
                duration_ms = int(duration_s * 1000)
                if slow_ms_threshold and duration_ms < slow_ms_threshold:
                    return

                end_cpu_times = proc.cpu_times()
                end_proc = get_proc_metrics(proc)
                end_sys = get_sys_metrics()
                end_gpu = get_gpu_metrics() if include_gpu else None

                cpu_delta = (end_cpu_times.user + end_cpu_times.system) - (start_cpu_times.user + start_cpu_times.system)
                cpu_count = psutil.cpu_count() or 1
                proc_cpu_percent = float((cpu_delta / duration_s) * 100.0 / cpu_count)

                payload: Dict[str, Any] = {
                    "event": "resource_monitor",
                    "tag": tag,
                    "function": fn.__name__,
                    "status": status,
                    "latency_ms": duration_ms,
                    **_find_request_context(args, kwargs),
                    "proc": {
                        "cpu_percent_window": round(proc_cpu_percent, 2),
                        "rss_mb_start": round(start_proc.rss_bytes / (1024**2), 2),
                        "rss_mb_end": round(end_proc.rss_bytes / (1024**2), 2),
                        "rss_mb_delta": round((end_proc.rss_bytes - start_proc.rss_bytes) / (1024**2), 2),
                        "threads": end_proc.threads,
                    },
                    "sys": {
                        "cpu_percent_now": round(end_sys.cpu_percent, 2),
                        "mem_percent": round(end_sys.mem_percent, 2),
                        "mem_used_gb": round(end_sys.mem_used_bytes / (1024**3), 3),
                        "mem_total_gb": round(end_sys.mem_total_bytes / (1024**3), 3),
                    },
                }

                if include_gpu:
                    payload["gpu_start"] = asdict(start_gpu) if start_gpu else None
                    payload["gpu_end"] = asdict(end_gpu) if end_gpu else None

                _structured_log(logger, logging.INFO if status == "ok" else logging.ERROR, payload)

        return async_wrapper if is_async else sync_wrapper

    return decorator

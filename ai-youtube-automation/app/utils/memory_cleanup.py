# app/middlewares/memory_cleanup.py
from __future__ import annotations
import gc
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class MemoryCleanupMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, include_gpu: bool = False, pre_gc: bool = True, post_gc: bool = True):
        super().__init__(app)
        self.include_gpu = include_gpu
        self.pre_gc = pre_gc
        self.post_gc = post_gc

    def _cleanup(self):
        gc.collect()

        if not self.include_gpu:
            return

        # GPU cleanup (best-effort)
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        except Exception:
            pass

        # If you use CuPy anywhere (optional)
        try:
            import cupy as cp
            cp.get_default_memory_pool().free_all_blocks()
            cp.get_default_pinned_memory_pool().free_all_blocks()
        except Exception:
            pass

    async def dispatch(self, request: Request, call_next):
        if self.pre_gc:
            self._cleanup()

        try:
            response = await call_next(request)
            return response
        finally:
            if self.post_gc:
                self._cleanup()

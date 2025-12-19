from fastapi import FastAPI
from .routers import (generate_voice, generate_thumbnail, 
                      generate_yt_video_script, generate_local_video_script,
                      voice_to_video_merge, merge_all_step_to_video)

from app.utils.memory_cleanup import MemoryCleanupMiddleware
app = FastAPI(title="AI Creator System")

app.add_middleware(
    MemoryCleanupMiddleware,
    include_gpu=True,   # set True only if you use GPU libs (torch/cupy)
    pre_gc=True,
    post_gc=True,
)

app.include_router(generate_voice.router)
app.include_router(generate_thumbnail.router)
app.include_router(generate_yt_video_script.router)
app.include_router(generate_local_video_script.router)
app.include_router(voice_to_video_merge.router)
app.include_router(merge_all_step_to_video.router)

@app.get("/")
def health():
    return {"status": "ok"}
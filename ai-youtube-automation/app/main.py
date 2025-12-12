from fastapi import FastAPI
from .routers import (publish, generate_voice, generate_thumbnail, story_explain, 
                      generate_yt_video_script, generate_local_video_script, yt_uploader, read_script,
                      voice_to_video_merge)

app = FastAPI(title="AI Creator System")

app.include_router(publish.router)
app.include_router(generate_voice.router)
app.include_router(generate_thumbnail.router)
app.include_router(story_explain.router)
app.include_router(generate_yt_video_script.router)
app.include_router(generate_local_video_script.router)
app.include_router(yt_uploader.router)
app.include_router(read_script.router)
app.include_router(voice_to_video_merge.router)

@app.get("/")
def health():
    return {"status": "ok"}
from fastapi import FastAPI
from .routers import publish, generate, share, generate_voice, generate_thumbnail, story_explain, generate_yt_video_script, generate_local_video_script

app = FastAPI(title="AI Creator System")

app.include_router(publish.router)
app.include_router(generate.router)
app.include_router(share.router)
app.include_router(generate_voice.router)
app.include_router(generate_thumbnail.router)
app.include_router(story_explain.router)
app.include_router(generate_yt_video_script.router)
app.include_router(generate_local_video_script.router)

@app.get("/")
def health():
    return {"status": "ok"}
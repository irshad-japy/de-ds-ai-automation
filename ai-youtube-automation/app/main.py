from fastapi import FastAPI
from .routers import publish, generate, share, generate_voice, generate_thumbnail, story_explain

app = FastAPI(title="AI Creator System")

app.include_router(publish.router)
app.include_router(generate.router)
app.include_router(share.router)
app.include_router(generate_voice.router)
app.include_router(generate_thumbnail.router)
app.include_router(story_explain.router)

@app.get("/")
def health():
    return {"status": "ok"}
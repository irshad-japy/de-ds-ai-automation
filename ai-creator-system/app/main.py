from fastapi import FastAPI
from .routers import publish, generate, share, orchestrate

app = FastAPI(title="AI Creator System")

app.include_router(publish.router)
app.include_router(generate.router)
app.include_router(share.router)
app.include_router(orchestrate.router)

@app.get("/")
def health():
    return {"status": "ok"}
from fastapi import FastAPI, UploadFile, HTTPException, APIRouter
from fastapi.responses import FileResponse
import tempfile, os
import nltk
nltk.download("punkt")
nltk.download("punkt_tab")

from ..services.generate_thumbnail import generate_thumbnail

router = APIRouter(prefix="/generate_thumbnail", tags=["generate"])

@router.post("/generate-thumbnail")
async def generate_thumbnail_api(file: UploadFile):
    """
    Accepts any text file (.txt, .py, .json, etc.) and returns a PNG thumbnail
    """
    try:
        suffix = os.path.splitext(file.filename or "input.txt")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="wb") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        output_path = f"output/{os.path.splitext(file.filename)[0]}_thumbnail.png"
        path = generate_thumbnail(tmp_path, output_path)

        return FileResponse(path, media_type="image/png", filename=os.path.basename(path))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

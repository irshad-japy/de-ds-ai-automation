from fastapi import FastAPI, HTTPException, Form, APIRouter
from googletrans import Translator
from app.services.generate_yt_video_script import extract_video_id, fetch_and_save_transcript

translator = Translator()

router = APIRouter(prefix="/script", tags=["generate"])

@router.post("/extract_script")
def extract_script(url: str = Form(...), lang: str = Form("hi")):
    """
    Extract YouTube transcript for the given URL and language,
    save to output folder, and return path.
    """
    try:
        video_id = extract_video_id(url)
        # Ensure languages is a list
        saved_path = fetch_and_save_transcript(url, languages=[lang])

        return {
            "video_id": video_id,
            "language": lang,
            "saved_file": saved_path,
            "message": "Transcript extracted and saved successfully."
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
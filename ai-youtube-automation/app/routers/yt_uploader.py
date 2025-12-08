# yt_api.py

from typing import List, Optional, Literal
from fastapi import FastAPI, HTTPException, Form, APIRouter
from pydantic import BaseModel, Field

from ..services.yt_uploader import (
    get_authenticated_service,
    upload_video,
    add_to_playlist,
    upload_captions,
)

router = APIRouter(prefix="/automation", tags=["YouTube Uploader API"])

# --------- Pydantic models --------- #

class CaptionItem(BaseModel):
    caption_file: str = Field(..., description="Full path to caption file (.srt/.vtt)")
    language: str = Field("en", description="Language code, e.g. 'en', 'hi'")
    name: Optional[str] = Field(None, description="Optional caption track name")
    is_draft: bool = Field(False, description="Upload captions as draft")

class UploadRequest(BaseModel):
    video_file: str = Field(..., description="Full path to local MP4 file")
    title: str = Field(..., description="Video title (max ~100 chars recommended)")
    description: str = Field("", description="Video description (max ~5000 chars)")
    tags: List[str] = Field(default_factory=list, description="List of tags")
    category_id: str = Field("27", description="YouTube category ID (default 27=Education)")
    privacy_status: Literal["public", "unlisted", "private"] = "public"
    default_language: Optional[str] = Field(
        None,
        description="Default language code, e.g. 'hi', 'en', 'en-IN'"
    )
    made_for_kids: bool = Field(False, description="Mark video as made for kids")
    recording_date: Optional[str] = Field(
        None,
        description="Recording date (YYYY-MM-DD or RFC3339)"
    )
    playlist_id: Optional[str] = Field(
        None,
        description="Playlist ID to add the video to (optional)"
    )
    captions: List[CaptionItem] = Field(
        default_factory=list,
        description="Optional list of caption tracks to upload"
    )

class UploadResponse(BaseModel):
    video_id: str
    playlist_item_ids: List[str] = Field(default_factory=list)
    caption_ids: List[str] = Field(default_factory=list)
    message: str = "Upload success"

# --------- Main upload endpoint --------- #

@router.post("/upload-video", response_model=UploadResponse)
def upload_video_endpoint(payload: UploadRequest):
    """
    Uploads a video using yt_uploader helpers and returns video ID + info.
    This is what you'll call from n8n.
    """
    try:
        # 1. Get authorized YouTube client (reuses token.json)
        youtube = get_authenticated_service()

        # 2. Upload video
        video_id = upload_video(
            youtube=youtube,
            video_file=payload.video_file,
            title=payload.title,
            description=payload.description,
            tags=payload.tags if payload.tags else None,
            category_id=payload.category_id,
            privacy_status=payload.privacy_status,
            default_language=payload.default_language,
            made_for_kids=payload.made_for_kids,
            recording_date=payload.recording_date,
        )

        playlist_item_ids: List[str] = []
        caption_ids: List[str] = []

        # 3. Add to playlist (optional)
        if payload.playlist_id:
            resp = add_to_playlist(youtube, video_id, payload.playlist_id)
            # our original add_to_playlist just prints; if you want IDs back,
            # you can modify it to return response. For now we just append a placeholder.
            playlist_item_ids.append("added_to_playlist")

        # 4. Upload captions (optional)
        for cap in payload.captions:
            resp = upload_captions(
                youtube=youtube,
                video_id=video_id,
                caption_file=cap.caption_file,
                language=cap.language,
                name=cap.name,
                is_draft=cap.is_draft,
                sync=True,  # good for transcript/simple SRT
            )
            # As with playlist, upload_captions prints; you can modify it to return caption_id
            caption_ids.append("caption_uploaded")

        return UploadResponse(
            video_id=video_id,
            playlist_item_ids=playlist_item_ids,
            caption_ids=caption_ids,
            message="YouTube upload completed successfully",
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # For debugging, you might want to log full traceback
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

from fastapi import APIRouter, HTTPException
from pathlib import Path
from ..schemas import ContentItem, TakeawaysResponse, ThumbnailResponse, NarrationResponse
from ..services import nlp, tts, thumbnail, audio
from ..utils.io import ensure_dir

router = APIRouter(prefix="/generate", tags=["generate"])

@router.post("/takeaways", response_model=TakeawaysResponse)
async def generate_takeaways(item: ContentItem):
    try:
        takeaways, keywords = nlp.extract_takeaways_and_keywords(item.article.body_markdown)
        hook_script = nlp.build_hook_script(item.article.title, takeaways)
        out_audio = ensure_dir(item.id, "hook.mp3")
        tts.tts_offline(hook_script, out_audio)
        # Save JSON files if needed
        return TakeawaysResponse(takeaways=takeaways, seo_keywords=keywords, hook_script=hook_script, hook_audio_path=str(out_audio))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/thumbnail", response_model=ThumbnailResponse)
async def generate_thumbnail(item: ContentItem):
    """
    Generate YouTube thumbnail for the given article.
    """
    try:
        # ✅ Get thumbnail spec safely
        spec = item.youtube.get("thumbnail_spec", {})

        # ✅ Generate output file path once
        out_path = ensure_dir(item.id, "thumbnail.png")

        # ✅ Ensure only the parent folder exists (not the file)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # ✅ Call thumbnail generator with a *Path*, not a folder name
        path = thumbnail.create_thumbnail(
            title=spec.get("title_text", item.article.title),
            subtitle=spec.get("sub_text", item.article.subtitle or ""),
            branding=spec.get("branding", ""),
            style=spec.get("style", ""),
            out_path=out_path,  # full file path like artifacts/<id>/thumbnail.png
        )

        return ThumbnailResponse(thumbnail_path=str(path))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/narration", response_model=NarrationResponse)
async def generate_narration(item: ContentItem):
    """
    Generate narration audio (MP3) from article text and optionally mix it with background music.
    """
    try:
        # ✅ Create directory-safe file path for narration
        narration_raw = ensure_dir(item.id, "narration_raw.mp3")

        # ✅ Generate offline TTS audio (save directly to narration_raw)
        tts.tts_offline(item.article.body_markdown, narration_raw)

        # ✅ If background music is provided, mix it with narration
        if getattr(item.media, "bg_music_path", None):
            out_mix = ensure_dir(item.id, "narration_mix.mp3")
            mixed = audio.mix_with_bg(narration_raw, Path(item.media.bg_music_path), out_mix)
            return NarrationResponse(narration_path=str(mixed))

        # ✅ Otherwise return raw narration file path
        return NarrationResponse(narration_path=str(narration_raw))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
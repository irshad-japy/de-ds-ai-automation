from fastapi import APIRouter, HTTPException
from ..utils.schemas import SocialResponse
from ..services.socials import post_linkedin, post_facebook_page, post_instagram_caption

router = APIRouter(prefix="/share", tags=["share"])

@router.post("/socials", response_model=SocialResponse)
async def share_socials(payload: dict):
    try:
        text = payload.get("text", "")
        link = payload.get("link", "")
        platforms = payload.get("platforms", ["linkedin"])

        results = {}
        if "linkedin" in platforms:
            results["linkedin"] = await post_linkedin(f"{text}\n{link}")
        if "facebook" in platforms:
            results["facebook"] = await post_facebook_page(text, link)
        if "instagram" in platforms:
            results["instagram"] = await post_instagram_caption(text, link)

        return SocialResponse(platform_results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
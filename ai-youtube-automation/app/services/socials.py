from ..utils.config import settings
import httpx

async def post_linkedin(text: str) -> dict:
    if not settings.LINKEDIN_ACCESS_TOKEN:
        return {"status": "skipped", "reason": "no token"}
    # Minimal sample (replace with full UGC Post call)
    headers = {"Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}"}
    # TODO: Implement full LinkedIn UGC API per docs
    print("LinkedIn posting placeholder executed")
    return {"status": "ok"}

async def post_facebook_page(message: str, link: str) -> dict:
    if not settings.FACEBOOK_PAGE_ACCESS_TOKEN or not settings.FACEBOOK_PAGE_ID:
        return {"status": "skipped", "reason": "no fb token/page"}
    page_id = settings.FACEBOOK_PAGE_ID
    url = f"https://graph.facebook.com/{page_id}/feed"
    params = {"message": message, "link": link, "access_token": settings.FACEBOOK_PAGE_ACCESS_TOKEN}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, params=params)
        r.raise_for_status()
    return r.json()

async def post_instagram_caption(caption: str, link: str) -> dict:
    if not settings.INSTAGRAM_ACCESS_TOKEN or not settings.INSTAGRAM_BUSINESS_ID:
        return {"status": "skipped", "reason": "no ig token/biz id"}
    # For links, IG requires bio/link-in-bio workflows; here we include caption only.
    print("Instagram posting placeholder executed")
    return {"status": "ok"}
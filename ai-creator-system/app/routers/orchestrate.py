from fastapi import APIRouter
from ..content_registry import CONTENT_ITEMS
from ..schemas import ContentItem
from .publish import publish_hashnode
from .generate import generate_takeaways, generate_thumbnail, generate_narration
from .share import share_socials
import re

router = APIRouter(prefix="/orchestrate", tags=["orchestrate"])

def sanitize_slug(title: str) -> str:
    """Convert title into a valid Hashnode slug"""
    slug = re.sub(r'[^a-z0-9-]', '-', title.lower())  # only lowercase, numbers, hyphen
    slug = re.sub(r'-+', '-', slug)                   # remove consecutive hyphens
    return slug.strip('-')                            # trim start/end hyphens

@router.post("/run")
async def run_pipeline():
    processed = []
    for raw in CONTENT_ITEMS:
        item = ContentItem(**raw)
        if not item.status.get("content_ready"):
            continue
        
        safe_slug = sanitize_slug(item.article.title)

        # Pass clean slug
        pub = await publish_hashnode(item, slug=safe_slug)

        tkv = await generate_takeaways(item)
        thumb = await generate_thumbnail(item)
        narr = await generate_narration(item)

        # share_payload = {
        #     "text": f"{item.article.title}\nTop takeaways: " + "; ".join(tkv.takeaways[:3]),
        #     "link": pub["post_url"],
        #     "platforms": item.distribution.share_to or ["linkedin"],
        # }
        # social = await share_socials(share_payload)

        processed.append({
            "id": item.id,
            "hashnode_url": pub["post_url"],
            "thumbnail": thumb.thumbnail_path,
            "narration": narr.narration_path,
            # "social": social.platform_results,
        })
    return {"processed": processed}

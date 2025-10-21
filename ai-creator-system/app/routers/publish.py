from fastapi import APIRouter, HTTPException
from ..schemas import PublishResponse, ContentItem
from ..services.hashnode import publish_to_hashnode

router = APIRouter(prefix="/publish", tags=["publish"])

@router.post("/hashnode", response_model=PublishResponse)
async def publish_hashnode(item: ContentItem, slug: str | None = None):
    """
    Publishes a given content item to Hashnode using a sanitized slug.
    """
    try:
        url, post_id = await publish_to_hashnode(
            title=item.article.title,
            body_markdown=item.article.body_markdown,
            tags=item.meta.tags or ["AI", "Python"],
            publication_id=None,
            slug=slug,   # ✅ forward cleaned slug
        )
        return {"post_url": url, "post_id": post_id}
    except Exception as e:
        print(f"Hashnode publish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

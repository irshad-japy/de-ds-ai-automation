from typing import Optional, List, Tuple, Dict
import httpx
from ..utils.config import settings
from ..utils.logging import logger

HASHNODE_ENDPOINT = "https://gql.hashnode.com"

# GraphQL queries
GET_PUBLICATION_QUERY = """
query Publication($host: String!) {
  publication(host: $host) {
    id
    title
  }
}
"""

PUBLISH_POST_MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post {
      id
      slug
      title
      url
    }
  }
}
"""

async def _get_publication_id() -> str:
    """Fetch the publication ID dynamically."""
    if not settings.HASHNODE_BLOG_HOST:
        raise RuntimeError("HASHNODE_BLOG_HOST not set in settings")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.HASHNODE_TOKEN}",
    }
    payload = {
        "query": GET_PUBLICATION_QUERY,
        "variables": {"host": settings.HASHNODE_BLOG_HOST},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(HASHNODE_ENDPOINT, json=payload, headers=headers)
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"Failed to get publicationId: {data['errors']}")
        return data["data"]["publication"]["id"]

async def publish_to_hashnode(
    title: str,
    body_markdown: str,
    tags: Optional[List[str]] = None,
    cover_image_url: Optional[str] = None,
    publication_id: Optional[str] = None,
    slug: Optional[str] = None
) -> Tuple[str, str]:
    """Publish post to Hashnode using GraphQL API."""
    if not settings.HASHNODE_TOKEN:
        raise RuntimeError("HASHNODE_TOKEN not set in settings")

    pub_id = publication_id or settings.HASHNODE_PUBLICATION_ID
    if not pub_id:
        pub_id = await _get_publication_id()

    # Format tags for Hashnode
    formatted_tags: List[Dict[str, str]] = []
    if tags:
        for tag in tags:
            tag_slug = tag.lower().replace(" ", "-")
            formatted_tags.append({"name": tag, "slug": tag_slug})

    # ✅ Use sanitized slug (fallback if missing)
    safe_slug = slug or title.lower().replace(" ", "-")
    safe_slug = safe_slug.replace("+", "-").replace("_", "-")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.HASHNODE_TOKEN}",
    }

    payload = {
        "query": PUBLISH_POST_MUTATION,
        "variables": {
            "input": {
                "title": title,
                "slug": safe_slug,
                "contentMarkdown": body_markdown,
                "tags": formatted_tags,
                "publicationId": pub_id,
            }
        },
    }

    if cover_image_url:
        payload["variables"]["input"]["coverImageURL"] = cover_image_url

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(HASHNODE_ENDPOINT, json=payload, headers=headers)
        logger.info(f"Hashnode raw response: {response.text}")

        try:
            response.raise_for_status()
        except Exception:
            raise RuntimeError(f"Hashnode HTTP error: {response.text}")

        data = response.json()
        if "errors" in data:
            raise RuntimeError(f"Hashnode GraphQL errors: {data['errors']}")

        post = data["data"]["publishPost"]["post"]
        return post["url"], post["id"]

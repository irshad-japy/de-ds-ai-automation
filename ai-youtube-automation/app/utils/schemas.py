from pydantic import BaseModel, Field
from typing import List, Optional

class Article(BaseModel):
    title: str
    subtitle: Optional[str] = None
    cover_image_path: Optional[str] = None
    body_markdown: str
    canonical_url: Optional[str] = None
    series: Optional[str] = None

class HookSpec(BaseModel):
    max_seconds: int = 30
    style: str = "energetic, concise, curiosity gap"
    cta: str = "Subscribe for weekly AI/data builds"

class ThumbnailSpec(BaseModel):
    title_text: str
    sub_text: str
    branding: str
    style: str = "high contrast, bold, minimal"

class Meta(BaseModel):
    topic: str
    tags: List[str] = []
    target_audience: str = "Beginner"
    tone: str = "practical"
    language: str = "en"

class Media(BaseModel):
    images: List[str] = []
    bg_music_path: Optional[str] = None

class Distribution(BaseModel):
    share_to: List[str] = []
    hashtags: List[str] = []

class ContentItem(BaseModel):
    id: str
    status: dict = Field(default_factory=lambda: {
    "content_ready": False,
    "hashnode_published": False,
    "yt_assets_ready": False,
    "social_shared": False,
    })
    meta: Meta
    article: Article
    media: Media = Media()
    youtube: dict = Field(default_factory=lambda: {
    "hook_spec": HookSpec().model_dump(),
    "thumbnail_spec": ThumbnailSpec(title_text="", sub_text="", branding="").model_dump()
    })
    distribution: Distribution = Distribution()

class PublishResponse(BaseModel):
    post_url: str
    post_id: str

class TakeawaysResponse(BaseModel):
    takeaways: List[str]
    seo_keywords: List[str]
    hook_script: str
    hook_audio_path: str

class ThumbnailResponse(BaseModel):
    thumbnail_path: str

class NarrationResponse(BaseModel):
    narration_path: str

class SocialResponse(BaseModel):
    platform_results: dict
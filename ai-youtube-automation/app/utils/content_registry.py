from .schemas import ContentItem, Meta, Article, Media, Distribution


CONTENT_ITEMS = [
    ContentItem(
    id="proj-2025-10-18-aws-glue-streaming",
    status={
        "content_ready": True,
        "hashnode_published": False,
        "yt_assets_ready": False,
        "social_shared": False,
    },
    meta=Meta(
        topic="AI/Data Engineering",
        tags=["AWS Glue", "PySpark", "Kinesis", "Streaming"],
        target_audience="Intermediate",
        tone="practical",
        language="en",
    ),
    article=Article(
        title="Real-time Event Pipelines with AWS Glue + Kinesis",
        subtitle="A practical guide with code, checkpoints, and DAGs",
        cover_image_path="assets/covers/glue_kinesis_cover.png",
        body_markdown="# Intro\nThis is where your full Markdown article goes...",
    ),
    media=Media(
        images=[
            "assets/diagrams/architecture.png",
            "assets/diagrams/checkpointing.png",
        ],
        bg_music_path="assets/audio/bg_lofi_01.mp3",
    ),
    distribution=Distribution(
        share_to=["linkedin", "facebook", "instagram"],
        hashtags=["#AWS", "#Glue", "#PySpark", "#Streaming", "#DataEngineering"],
        ),
    ).model_dump()
]
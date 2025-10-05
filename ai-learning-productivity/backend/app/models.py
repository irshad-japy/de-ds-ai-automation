from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal

class POCInput(BaseModel):
    poc_key: str
    title: str
    goal: str
    context: Optional[str] = ""
    steps_taken: List[str] = []
    commands: List[str] = []
    issues: List[str] = []
    fixes: List[str] = []
    outcome: Optional[str] = ""
    time_spent_mins: Optional[int] = 0
    tags: List[str] = []
    links: List[str] = []
    notes: Optional[str] = ""

class SummarizeOutput(BaseModel):
    poc_key: str
    tldr: str
    summary_bullets: List[str]
    kb_markdown: str
    voiceover_script: str
    image_briefs: List[Dict[str, str]]
    safety_redactions: List[str] = []

class KBIngest(BaseModel):
    mode: Literal["ingest","answer"]
    poc_key: str
    unique_tag: Optional[str] = None
    docs: Optional[List[Dict[str, str]]] = None
    metadata: Optional[Dict[str, Any]] = None
    # answer mode:
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    poc_key_hint: Optional[str] = None
    max_tokens: Optional[int] = 600

class KBIngestResult(BaseModel):
    poc_key: str
    status: str
    chunks_indexed: int = 0
    chunk_ids: List[str] = []
    metadata_applied: Dict[str, Any] = {}

class KBAnswerResult(BaseModel):
    answer_markdown: str
    citations: List[Dict[str, str]]
    retrieval_debug: Dict[str, Any]

class TranscriptSpan(BaseModel):
    t0: float
    t1: float
    text: str

class OCRSpan(BaseModel):
    t0: float
    t1: float
    bbox: List[int]
    text: str

class RedactionPolicy(BaseModel):
    actions: List[str] = ["blur","strike","mute","bleep"]
    sensitive_terms_extra: List[str] = []

class MediaRedactIn(BaseModel):
    poc_key: str
    video_meta: Dict[str, Any]
    transcript: List[TranscriptSpan] = []
    ocr_spans: List[OCRSpan] = []
    redaction_policy: RedactionPolicy = RedactionPolicy()

class MediaRedactOut(BaseModel):
    poc_key: str
    audio_ops: List[Dict[str, Any]]
    video_ops: List[Dict[str, Any]]
    text_ops: List[Dict[str, Any]]
    export: Dict[str, Any]
    sensitive_hits_report: List[str] = []
    notes: Optional[str] = ""

class PublishIn(BaseModel):
    poc_key: str
    video_file: str
    summary: str
    kb_permalink: str
    scheduled_time_ist: str
    audience: str

class PublishOut(BaseModel):
    poc_key: str
    youtube: Dict[str, Any]
    social_posts: Dict[str, str]
    schedule_plan: Dict[str, Any]

class KBLinkIn(BaseModel):
    poc_key: str
    youtube_url: str
    published_at: str
    channels: List[str]

class KBLinkOut(BaseModel):
    poc_key: str
    updated_fields: List[str]
    status: str

from fastapi import FastAPI
from .models import *
from .llm import simple_llm_summarize
from .vector_store import ingest_docs, search
from .redact import sensitive_hits
from .utils import mk_kb_markdown

app = FastAPI(title="AI Learning Backend", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/summarize", response_model=SummarizeOutput)
async def summarize(poc: POCInput):
    llm = await simple_llm_summarize(poc.model_dump())
    kb_md = mk_kb_markdown(poc.model_dump(), llm["tldr"], llm["bullets"])
    out = SummarizeOutput(
        poc_key=poc.poc_key,
        tldr=llm["tldr"],
        summary_bullets=llm["bullets"],
        kb_markdown=kb_md,
        voiceover_script=llm["voiceover"],
        image_briefs=[
            {"title":"Local RAG diagram","description":"Docs→Embed→Qdrant→RAG→LLM answer"},
            {"title":"POC stack","description":"Minimal components & ports"}
        ],
        safety_redactions=[]
    )
    return out

@app.post("/kb", response_model=KBIngestResult|KBAnswerResult)
def kb(req: KBIngest):
    if req.mode == "ingest":
        docs = req.docs or []
        md = req.metadata or {}
        if req.unique_tag: md["unique_tag"] = req.unique_tag
        prepared = ingest_docs(req.poc_key, docs, md)
        return KBIngestResult(
            poc_key=req.poc_key, status="ok",
            chunks_indexed=len(prepared),
            chunk_ids=[p["id"] for p in prepared],
            metadata_applied=md
        )
    else:
        flt = req.filters or {}
        if req.poc_key_hint: flt["poc_key"] = req.poc_key_hint
        res = search(req.query or "", flt, top_k=6)
        # simple synthesis: return top snippet references
        citations = []
        snips = []
        for r in res:
            pl = r.payload
            citations.append({
                "poc_key": pl.get("poc_key",""),
                "chunk_id": str(r.id),
                "doc_id": pl.get("doc_id","")
            })
            snips.append(f"• {pl.get('doc_id','')}#{pl.get('chunk_index',0)}")
        answer = "Top relevant notes:\n" + "\n".join(snips) + "\n\nUse filters for exact POC key."
        return KBAnswerResult(
            answer_markdown=answer,
            citations=citations,
            retrieval_debug={"top_k": 6, "filters_used": flt}
        )

@app.post("/media/redact", response_model=MediaRedactOut)
def media_redact(req: MediaRedactIn):
    # Combine transcript + OCR to find hits
    full_text = "\n".join([s.text for s in req.transcript] + [o.text for o in req.ocr_spans])
    hits = sensitive_hits(full_text, req.redaction_policy.sensitive_terms_extra)

    audio_ops = [{"type":"denoise","range":[0, req.video_meta.get("duration_sec",0)]},
                 {"type":"declick","range":[0, req.video_meta.get("duration_sec",0)]}]
    text_ops = []
    video_ops = []
    # Example: if pattern sk-... in transcript, add a bleep between the first span that contains it
    for s in req.transcript:
        if any(h in s.text for h in hits):
            audio_ops.append({"type":"bleep","range":[s.t0, s.t1]})
            text_ops.append({"type":"redact_transcript","t0":s.t0,"t1":s.t1,"pattern":"SENSITIVE"})
    for o in req.ocr_spans:
        if any(h in o.text for h in hits):
            video_ops.append({"type":"blur","range":[o.t0,o.t1],"bbox":o.bbox})

    return MediaRedactOut(
        poc_key=req.poc_key,
        audio_ops=audio_ops,
        video_ops=video_ops,
        text_ops=text_ops,
        export={
            "safe_filename": f"{req.poc_key}_safe.mp4",
            "burn_captions": True,
            "thumbnail_hint": "Pick a frame with architecture diagram"
        },
        sensitive_hits_report=hits,
        notes="Apply mild NR; preserve voice clarity."
    )

@app.post("/publish/schedule", response_model=PublishOut)
def publish(req: PublishIn):
    yt = {
        "title": f"{req.summary[:55]}",
        "description": f"{req.summary}\n\nKB: {req.kb_permalink}\nTags: rag, llm, local, qdrant, ollama",
        "thumbnail_text_options": ["FREE LOCAL RAG","OLLAMA + QDRANT","NO API COSTS"],
        "visibility": "public",
        "language": "en",
        "category": "Education"
    }
    posts = {
        "linkedin": f"Built a FREE local RAG — watch: <YOUTUBE_URL>  #Ollama #Qdrant #RAG #LLM #DevTools",
        "instagram_caption": "Local RAG, zero API cost. Watch: <YOUTUBE_URL>\n#ollama #qdrant #rag #ai #coding"
    }
    plan = {
        "when": req.scheduled_time_ist,
        "steps": ["upload_youtube", "get_youtube_url", "post_linkedin", "post_instagram"]
    }
    return PublishOut(poc_key=req.poc_key, youtube=yt, social_posts=posts, schedule_plan=plan)

@app.post("/kb/link", response_model=KBLinkOut)
def kb_link(req: KBLinkIn):
    # In a real system, you'd upsert metadata in your DB; here we just ack
    return KBLinkOut(poc_key=req.poc_key, updated_fields=["youtube_url","published_at","channels"], status="linked")

def run():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

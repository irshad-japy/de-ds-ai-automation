# Controlled failure drills

Run at least one and capture the error + recovery evidence.

## Safest drill: malformed event

```powershell
poetry run python -m ingestion.events.send_malformed_event
```

Expected: the schema validator rejects it locally before Event Hubs. Recovery: add the missing required fields and resend valid events.

## Unsupported RAG question
Ask a question absent from the indexed sources, for example:

```powershell
poetry run python -m ai.rag.rag_answer "What is the company's vacation policy?"
```

Expected: the answer should say it is unsupported by the provided context.

## Storage permission drill (advanced)
Temporarily remove your Storage Blob Data Contributor assignment, run `ingestion.batch.upload_orders`, capture the authorization failure, restore the role, and rerun successfully. Avoid this if the resource is shared with teammates.

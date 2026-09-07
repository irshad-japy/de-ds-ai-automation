# Troubleshooting — POC-05

## 1. `az` is not recognized

Azure CLI is a separate Windows program. Installing Python packages such as `azure-identity` does not install the `az` command.

Fix:

1. Install Azure CLI.
2. Close terminal windows.
3. Open a new terminal.
4. Run `az version`.
5. Restart Windows if PATH has not refreshed.

## 2. `ModuleNotFoundError: No module named 'azure'`

Activate the virtual environment and install requirements:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. PowerShell says running scripts is disabled

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Or use Command Prompt and `activate.bat`.

## 4. Azure AI Search 401

Likely causes:

- wrong admin key;
- key copied from a different Search service;
- incorrect endpoint;
- key authentication disabled.

Check `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_ADMIN_KEY`, and Search service authentication settings.

## 5. Azure AI Search 403 with Entra ID

Likely RBAC issue. Confirm your user/managed identity has the correct Search roles. RBAC changes can take a few minutes to propagate.

## 6. Foundry 401/403

Check:

- correct base URL;
- correct resource key when using key mode;
- `az login` when using Entra mode;
- model-access RBAC role;
- resource networking/firewall rules.

## 7. Model/deployment not found

Your `.env` must contain the **deployment name**, not merely the model family name.

Example:

```dotenv
FOUNDRY_CHAT_DEPLOYMENT=rag-chat
```

if the deployment was named `rag-chat` in the portal.

## 8. 404 from Foundry endpoint

Verify that the base URL ends in the OpenAI-compatible v1 path displayed by the resource, usually `/openai/v1/`. Do not mix the project endpoint (`.../api/projects/...`) with an embedding endpoint. Embeddings should use the model inference/OpenAI v1 endpoint.

## 9. Embedding dimension mismatch

Typical error: Search rejects `content_vector` because the vector length does not match the index schema.

Fix:

1. Find the actual embedding output length.
2. Set `EMBEDDING_DIMENSIONS` correctly.
3. Run:

```powershell
python scripts/delete_index.py
python -m rag.ingest
```

If you intentionally request a reduced dimension from a `text-embedding-3-*` model, set:

```dotenv
EMBEDDING_REQUEST_DIMENSIONS=true
```

## 10. Search index schema cannot be updated

Some field/schema changes cannot be applied in place. Delete the POC index and recreate it:

```powershell
python scripts/delete_index.py
python -m rag.ingest
```

## 11. Free tier is unavailable

A subscription is limited in how many free services it can have, and availability can differ by region. Check whether an old free Search service already exists. If you select a paid tier, review costs first and delete it when finished.

## 12. Foundry model quota unavailable

Choose another available model or region, or request quota. Update the deployment names in `.env`. This POC does not require one exact chat model as long as your selected model supports the OpenAI-compatible chat API and your embedding model produces vectors of the configured size.

## 13. Retrieval is poor

Try:

- hybrid instead of vector-only;
- top-k 3, 5, or 10;
- smaller chunks;
- larger chunks;
- less/more overlap;
- cleaner document titles and metadata;
- adding a metadata filter;
- verifying the embedding model is the same during indexing and query time.

## 14. RAG answer uses outside knowledge

The system prompt forbids it, but no prompt is a mathematical guarantee. Strengthen production mitigation with retrieval confidence checks, evaluation, content versioning, structured citation validation, and model/prompt testing.

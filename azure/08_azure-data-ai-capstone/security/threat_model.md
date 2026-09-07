# Lightweight threat model

## Assets
- Raw and curated retail data.
- Search index content and embeddings.
- Model/agent endpoints.
- Infrastructure credentials and API keys.

## Main threats and controls
1. **Secret leakage** — `.env` is gitignored; production secrets belong in Key Vault/service connections/federated identity.
2. **Over-privileged identities** — separate Sender/Receiver/Reader/Contributor roles and keep agent tools read-only.
3. **Prompt injection / unsupported questions** — RAG prompt is constrained to retrieved context and returns "unsupported" when grounding is absent.
4. **Data poisoning / malformed events** — event schema validation rejects incomplete payloads before Bronze write.
5. **Accidental resource writes from AI** — the demo assistant exposes only retrieval/metric/scoring functions, no update/delete capability.
6. **Cost runaway** — Databricks/ML compute is optional; Search/Foundry deployments are cleaned up after the lab.

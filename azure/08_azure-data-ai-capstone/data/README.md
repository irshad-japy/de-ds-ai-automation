# Synthetic data

This POC deliberately uses synthetic retail data only.

- `orders_001.csv` — batch ingestion input.
- `shipment_events.jsonl` — real-time Event Hubs input.
- `policies.json` — RAG knowledge documents.
- `invoice_001.pdf` — synthetic invoice for Document Intelligence.

Regenerate CSV/JSON inputs with:

```powershell
poetry run python -m scripts.generate_synthetic_data
```

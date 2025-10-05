from lr.config import settings
from lr.vector.qdrant_store import client

if settings.qdrant_collection in [c.name for c in client.get_collections().collections]:
    client.delete_collection(settings.qdrant_collection)
    print("Deleted collection:", settings.qdrant_collection)
else:
    print("Collection not found:", settings.qdrant_collection)

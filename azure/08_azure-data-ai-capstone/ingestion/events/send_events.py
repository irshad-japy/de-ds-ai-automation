from __future__ import annotations

import argparse
import json
from pathlib import Path

from azure.eventhub import EventData, EventHubProducerClient

from common.auth import get_token_credential
from common.config import Settings
from ingestion.events.schema import validate_event


def producer() -> EventHubProducerClient:
    s = Settings()
    if s.eventhub_connection_string:
        return EventHubProducerClient.from_connection_string(
            conn_str=s.eventhub_connection_string, eventhub_name=s.eventhub_name
        )
    if not s.eventhub_namespace:
        raise RuntimeError("Set EVENTHUB_FULLY_QUALIFIED_NAMESPACE or EVENTHUB_CONNECTION_STRING")
    return EventHubProducerClient(
        fully_qualified_namespace=s.eventhub_namespace,
        eventhub_name=s.eventhub_name,
        credential=get_token_credential(),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="data/synthetic/shipment_events.jsonl")
    args = parser.parse_args()
    events = []
    for line in Path(args.file).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        validate_event(event)
        events.append(event)

    client = producer()
    with client:
        batch = client.create_batch()
        for event in events:
            batch.add(EventData(json.dumps(event)))
        client.send_batch(batch)
    print(f"[SUCCESS] Sent {len(events)} shipment events to Event Hubs")


if __name__ == "__main__":
    main()

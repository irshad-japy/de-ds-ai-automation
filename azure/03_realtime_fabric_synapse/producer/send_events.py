"""Send synthetic shipment events to Azure Event Hubs.

Beginner-friendly behavior:
- sends normal events;
- periodically resends a previous event_id to demonstrate deduplication;
- periodically generates an older event_ts to demonstrate watermark/late events.

Secrets are read from environment variables. Never commit a real Event Hubs key.
"""

import argparse
import json
import os
import random
import time
import uuid
from datetime import datetime, timedelta, timezone

from azure.eventhub import EventData, EventHubProducerClient
from dotenv import load_dotenv

load_dotenv()

EVENT_TYPES = ["CREATED", "PACKED", "SHIPPED", "IN_TRANSIT", "DELIVERED", "DELAYED"]
REGIONS = ["IN-SOUTH", "IN-NORTH", "IN-WEST", "IN-EAST"]


def utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def build_event(i: int, late: bool = False, event_id: str | None = None) -> dict:
    now = datetime.now(timezone.utc)
    if late:
        # Older than the 10-minute watermark used in the Databricks sample.
        now = now - timedelta(minutes=20)

    event_type = random.choices(
        EVENT_TYPES,
        weights=[10, 15, 25, 15, 25, 10],
        k=1,
    )[0]

    order_id = 1000 + (i % 75)
    revenue = round(random.uniform(250, 5000), 2)
    fulfillment_minutes = random.randint(10, 720)

    return {
        "event_id": event_id or f"evt-{uuid.uuid4().hex[:12]}",
        "order_id": order_id,
        "event_type": event_type,
        "event_ts": utc_iso(now),
        "region": random.choice(REGIONS),
        "revenue": revenue,
        "fulfillment_minutes": fulfillment_minutes,
        "producer_seq": i,
    }


def send_events(count: int, delay: float, duplicate_every: int, late_every: int) -> None:
    conn = os.getenv("EVENT_HUB_CONNECTION_STRING")
    hub = os.getenv("EVENT_HUB_NAME")

    if not conn or not hub:
        raise SystemExit(
            "Missing EVENT_HUB_CONNECTION_STRING or EVENT_HUB_NAME. "
            "Copy .env.example to .env and fill in your values."
        )

    producer = EventHubProducerClient.from_connection_string(
        conn_str=conn,
        eventhub_name=hub,
    )

    previous_event = None
    sent = 0
    duplicates = 0
    late_events = 0

    print(f"Sending {count} events to Event Hub: {hub}")
    print("Press Ctrl+C to stop early.\n")

    try:
        with producer:
            for i in range(1, count + 1):
                is_duplicate = duplicate_every > 0 and i % duplicate_every == 0 and previous_event
                is_late = late_every > 0 and i % late_every == 0

                if is_duplicate:
                    payload = dict(previous_event)
                    payload["producer_seq"] = i
                    duplicates += 1
                    marker = "DUPLICATE"
                else:
                    payload = build_event(i, late=is_late)
                    if is_late:
                        late_events += 1
                        marker = "LATE"
                    else:
                        marker = "NORMAL"
                    previous_event = dict(payload)

                body = json.dumps(payload)
                event = EventData(body)

                # Partition by region. This preserves ordering per region but can create
                # uneven partitions if one region dominates production traffic.
                producer.send_event(event, partition_key=payload["region"])

                sent += 1
                print(
                    f"[{sent:03d}/{count:03d}] {marker:<9} "
                    f"id={payload['event_id']} type={payload['event_type']:<10} "
                    f"region={payload['region']} ts={payload['event_ts']}"
                )

                if delay > 0:
                    time.sleep(delay)
    except KeyboardInterrupt:
        print("\nStopped by user.")

    print("\nSummary")
    print(f"  sent attempts : {sent}")
    print(f"  duplicates    : {duplicates}")
    print(f"  late events   : {late_events}")
    print("Check Event Hubs > Monitoring > Metrics > Incoming Messages.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=int(os.getenv("EVENT_COUNT", "200")))
    parser.add_argument("--delay", type=float, default=float(os.getenv("EVENT_DELAY_SECONDS", "0.15")))
    parser.add_argument("--duplicate-every", type=int, default=int(os.getenv("DUPLICATE_EVERY", "25")))
    parser.add_argument("--late-every", type=int, default=int(os.getenv("LATE_EVENT_EVERY", "40")))
    args = parser.parse_args()

    send_events(args.count, args.delay, args.duplicate_every, args.late_every)


if __name__ == "__main__":
    main()

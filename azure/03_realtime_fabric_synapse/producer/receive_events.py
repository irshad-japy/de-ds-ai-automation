"""Simple local Event Hubs receiver used only for beginner verification.

Use a dedicated consumer group if you do not want this test receiver to
compete with another consumer in the same consumer group.
"""

import argparse
import json
import os
from datetime import datetime, timezone

from azure.eventhub import EventHubConsumerClient
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-events", type=int, default=20)
    parser.add_argument("--starting-position", default="-1",
                        help="'-1' = beginning, '@latest' = only new events")
    args = parser.parse_args()

    conn = os.getenv("EVENT_HUB_CONNECTION_STRING")
    hub = os.getenv("EVENT_HUB_NAME")
    group = os.getenv("EVENT_HUB_CONSUMER_GROUP", "$Default")

    if not conn or not hub:
        raise SystemExit("Missing EVENT_HUB_CONNECTION_STRING or EVENT_HUB_NAME in .env")

    received = 0
    client = None

    def on_event(partition_context, event):
        nonlocal received, client
        received += 1

        try:
            payload = json.loads(event.body_as_str(encoding="UTF-8"))
        except Exception:
            payload = {"raw": event.body_as_str()}

        print(
            f"[{received:03d}] partition={partition_context.partition_id} "
            f"offset={event.offset} sequence={event.sequence_number} payload={payload}"
        )

        partition_context.update_checkpoint(event)

        if received >= args.max_events and client:
            client.close()

    client = EventHubConsumerClient.from_connection_string(
        conn_str=conn,
        consumer_group=group,
        eventhub_name=hub,
    )

    print(
        f"Receiving up to {args.max_events} events from {hub} "
        f"(consumer group={group}, starting_position={args.starting_position})"
    )

    with client:
        client.receive(
            on_event=on_event,
            starting_position=args.starting_position,
        )


if __name__ == "__main__":
    main()

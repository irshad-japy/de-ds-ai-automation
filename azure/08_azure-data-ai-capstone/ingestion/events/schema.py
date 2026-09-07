from __future__ import annotations

REQUIRED_FIELDS = {"event_id", "order_id", "status", "event_time", "location"}


def validate_event(event: dict) -> None:
    missing = REQUIRED_FIELDS.difference(event)
    if missing:
        raise ValueError(f"Malformed shipment event. Missing: {sorted(missing)}")
    if not str(event["event_id"]).strip() or not str(event["order_id"]).strip():
        raise ValueError("event_id and order_id cannot be blank")

from __future__ import annotations

from ingestion.events.schema import validate_event


def main() -> None:
    bad_event = {"event_id": "BAD-001", "status": "BROKEN"}
    try:
        validate_event(bad_event)
    except ValueError as exc:
        print(f"[EXPECTED FAILURE] {exc}")
        print("[RECOVERY] Fix the payload by adding order_id, event_time, and location before sending.")
        return
    raise RuntimeError("Failure drill did not fail as expected")


if __name__ == "__main__":
    main()

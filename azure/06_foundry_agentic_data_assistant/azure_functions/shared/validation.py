from datetime import date


class ValidationError(ValueError):
    pass


def iso_date(value: str | None, name: str) -> str:
    if not value:
        raise ValidationError(f"Missing query parameter: {name}")
    try:
        return date.fromisoformat(value).isoformat()
    except Exception as exc:
        raise ValidationError(f"{name} must be YYYY-MM-DD") from exc


def date_range(start_value: str | None, end_value: str | None) -> tuple[str, str]:
    start = date.fromisoformat(iso_date(start_value, "start_date"))
    end = date.fromisoformat(iso_date(end_value, "end_date"))
    if start > end:
        raise ValidationError("start_date must be on or before end_date")
    if (end - start).days > 366:
        raise ValidationError("date range cannot exceed 366 days")
    return start.isoformat(), end.isoformat()


def order_id(value: str | None) -> int:
    if value is None:
        raise ValidationError("Missing query parameter: order_id")
    try:
        oid = int(value)
    except Exception as exc:
        raise ValidationError("order_id must be an integer") from exc
    if oid <= 0 or oid > 2_147_483_647:
        raise ValidationError("order_id is outside the allowed range")
    return oid


def metric_name(value: str | None) -> str:
    allowed = {"revenue", "delayed_shipments"}
    normalized = (value or "").strip().lower()
    if normalized not in allowed:
        raise ValidationError(f"metric_name must be one of: {', '.join(sorted(allowed))}")
    return normalized

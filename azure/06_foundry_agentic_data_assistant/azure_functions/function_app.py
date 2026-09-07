from __future__ import annotations

import json
import logging
import os
from datetime import date, datetime
from decimal import Decimal

import azure.functions as func

from shared.mock_repository import MockRepository
from shared.sql_repository import SqlRepository
from shared.validation import ValidationError, date_range, iso_date, metric_name, order_id

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def _repo():
    backend = os.getenv("DATA_BACKEND", "mock").strip().lower()
    if backend == "mock":
        return MockRepository()
    if backend == "azure_sql":
        return SqlRepository()
    raise RuntimeError("DATA_BACKEND must be 'mock' or 'azure_sql'")


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _response(payload, status=200):
    return func.HttpResponse(
        json.dumps(payload, default=_json_default),
        status_code=status,
        mimetype="application/json",
    )


def _handle(callable_):
    try:
        return _response(callable_())
    except ValidationError as exc:
        return _response({"error": "validation_error", "message": str(exc)}, 400)
    except Exception as exc:
        logging.exception("Tool endpoint failed")
        return _response({"error": "internal_error", "message": "Tool execution failed safely."}, 500)


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    return _response({"status": "ok", "service": "poc06-readonly-data-tools", "backend": os.getenv("DATA_BACKEND", "mock")})


@app.route(route="revenue-by-region", methods=["GET"])
def revenue_by_region(req: func.HttpRequest) -> func.HttpResponse:
    def run():
        start, end = date_range(req.params.get("start_date"), req.params.get("end_date"))
        rows = _repo().revenue_by_region(start, end)
        return {"tool": "get_revenue_by_region", "source": "azure_sql:dbo.usp_GetRevenueByRegion", "start_date": start, "end_date": end, "rows": rows}
    return _handle(run)


@app.route(route="delayed-shipments", methods=["GET"])
def delayed_shipments(req: func.HttpRequest) -> func.HttpResponse:
    def run():
        report_date = iso_date(req.params.get("date"), "date")
        rows = _repo().delayed_shipments(report_date)
        return {"tool": "get_delayed_shipments", "source": "azure_sql:dbo.usp_GetDelayedShipments", "report_date": report_date, "count": len(rows), "rows": rows}
    return _handle(run)


@app.route(route="order-summary", methods=["GET"])
def order_summary(req: func.HttpRequest) -> func.HttpResponse:
    def run():
        oid = order_id(req.params.get("order_id"))
        row = _repo().order_summary(oid)
        return {"tool": "get_order_summary", "source": "azure_sql:dbo.usp_GetOrderSummary", "found": row is not None, "order": row}
    return _handle(run)


@app.route(route="metric-source", methods=["GET"])
def metric_source(req: func.HttpRequest) -> func.HttpResponse:
    def run():
        metric = metric_name(req.params.get("metric_name"))
        row = _repo().metric_source(metric)
        return {"tool": "get_metric_source", "source": "azure_sql:dbo.usp_GetMetricSource", "metric": row}
    return _handle(run)

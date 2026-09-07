from azure.ai.projects.models import FunctionTool


def build_function_tools() -> list[FunctionTool]:
    return [
        FunctionTool(
            name="get_revenue_by_region",
            description="Get authoritative revenue grouped by region for an inclusive date range. Use for numeric revenue questions; never guess revenue from documents.",
            parameters={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Inclusive start date in YYYY-MM-DD format."},
                    "end_date": {"type": "string", "description": "Inclusive end date in YYYY-MM-DD format."},
                },
                "required": ["start_date", "end_date"],
                "additionalProperties": False,
            },
            strict=True,
        ),
        FunctionTool(
            name="get_delayed_shipments",
            description="Get authoritative delayed shipments for one calendar date.",
            parameters={
                "type": "object",
                "properties": {
                    "report_date": {"type": "string", "description": "Date in YYYY-MM-DD format."}
                },
                "required": ["report_date"],
                "additionalProperties": False,
            },
            strict=True,
        ),
        FunctionTool(
            name="get_order_summary",
            description="Get the read-only authoritative summary for one order ID, including current shipment status and recorded delay reason if present.",
            parameters={
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer", "minimum": 1, "description": "Positive order ID."}
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
            strict=True,
        ),
        FunctionTool(
            name="get_metric_source",
            description="Get the governed source/definition for a supported business metric.",
            parameters={
                "type": "object",
                "properties": {
                    "metric_name": {"type": "string", "enum": ["revenue", "delayed_shipments"]}
                },
                "required": ["metric_name"],
                "additionalProperties": False,
            },
            strict=True,
        ),
    ]

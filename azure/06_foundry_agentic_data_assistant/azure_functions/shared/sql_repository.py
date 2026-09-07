"""Azure SQL repository with an intentionally tiny, fixed interface.

There is deliberately NO execute_sql(sql) method in this class.
Every call executes one predefined stored procedure with bound parameters.
"""

from __future__ import annotations

import os
import struct
from typing import Any

import pyodbc
from azure.identity import DefaultAzureCredential

SQL_COPT_SS_ACCESS_TOKEN = 1256


class SqlRepository:
    def __init__(self):
        server = os.environ["AZURE_SQL_SERVER"]
        database = os.environ["AZURE_SQL_DATABASE"]
        driver = os.getenv("AZURE_SQL_ODBC_DRIVER", "ODBC Driver 18 for SQL Server")
        self.connection_string = (
            f"Driver={{{driver}}};"
            f"Server=tcp:{server},1433;"
            f"Database={database};"
            "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        self.credential = DefaultAzureCredential()

    def _connect(self):
        token = self.credential.get_token("https://database.windows.net/.default").token
        token_bytes = token.encode("utf-16-le")
        token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
        return pyodbc.connect(self.connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})

    @staticmethod
    def _rows(cursor) -> list[dict[str, Any]]:
        columns = [col[0] for col in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in cursor.fetchall()] if columns else []

    def revenue_by_region(self, start_date: str, end_date: str):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("EXEC dbo.usp_GetRevenueByRegion @StartDate=?, @EndDate=?", start_date, end_date)
            return self._rows(cur)

    def delayed_shipments(self, report_date: str):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("EXEC dbo.usp_GetDelayedShipments @ReportDate=?", report_date)
            return self._rows(cur)

    def order_summary(self, order_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("EXEC dbo.usp_GetOrderSummary @OrderId=?", order_id)
            rows = self._rows(cur)
            return rows[0] if rows else None

    def metric_source(self, metric_name: str):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("EXEC dbo.usp_GetMetricSource @MetricName=?", metric_name)
            rows = self._rows(cur)
            return rows[0] if rows else None

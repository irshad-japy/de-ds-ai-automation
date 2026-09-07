from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


def main() -> None:
    try:
        import pyodbc
    except ImportError as exc:
        raise RuntimeError("Run: poetry install --with sql") from exc

    conn_str = os.getenv("AZURE_SQL_ODBC_CONNECTION_STRING", "").strip()
    if not conn_str:
        raise RuntimeError("Set AZURE_SQL_ODBC_CONNECTION_STRING in .env")
    frame = pd.read_csv(Path("output/gold/customer_metrics.csv"))
    with pyodbc.connect(conn_str) as conn:
        cur = conn.cursor()
        for row in frame.itertuples(index=False):
            cur.execute(
                """
                MERGE dbo.customer_metrics AS t
                USING (SELECT ? customer_id, ? total_orders, ? total_units, ? total_revenue) AS s
                ON t.customer_id = s.customer_id
                WHEN MATCHED THEN UPDATE SET total_orders=s.total_orders, total_units=s.total_units,
                    total_revenue=s.total_revenue, refreshed_at=SYSUTCDATETIME()
                WHEN NOT MATCHED THEN INSERT(customer_id,total_orders,total_units,total_revenue)
                    VALUES(s.customer_id,s.total_orders,s.total_units,s.total_revenue);
                """,
                row.customer_id,
                int(row.total_orders),
                int(row.total_units),
                float(row.total_revenue),
            )
        conn.commit()
    print(f"[SUCCESS] Refreshed Azure SQL with {len(frame)} Gold customer rows")


if __name__ == "__main__":
    main()

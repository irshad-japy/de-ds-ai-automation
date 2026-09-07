SELECT COUNT(*) AS header_count FROM dbo.invoice_header;
SELECT COUNT(*) AS line_count FROM dbo.invoice_line;

SELECT TOP (20)
    invoice_key, invoice_number, invoice_date, supplier_name, customer_name,
    currency, subtotal, tax, total, source_blob, processed_at
FROM dbo.invoice_header
ORDER BY invoice_key;

SELECT
    h.invoice_number,
    h.subtotal,
    SUM(COALESCE(l.amount, l.quantity * l.unit_price)) AS calculated_line_sum,
    h.total
FROM dbo.invoice_header h
LEFT JOIN dbo.invoice_line l ON h.invoice_key = l.invoice_key
GROUP BY h.invoice_number, h.subtotal, h.total
ORDER BY h.invoice_number;

-- Idempotency check: should return zero rows.
SELECT source_hash, COUNT(*) AS duplicate_count
FROM dbo.invoice_header
GROUP BY source_hash
HAVING COUNT(*) > 1;

from src.validate_invoice import validate_invoice

def valid_invoice():
    return {
        "invoice_number": "SYN-1",
        "invoice_date": "2026-08-20",
        "supplier_name": "Synthetic Vendor",
        "subtotal": 100.0,
        "tax": 18.0,
        "total": 118.0,
        "line_items": [{"amount": 100.0}],
        "confidence": {
            "invoice_number": 0.99,
            "invoice_date": 0.99,
            "supplier_name": 0.99,
            "subtotal": 0.99,
            "total": 0.99,
        },
    }

def test_valid_invoice_passes():
    result = validate_invoice(valid_invoice())
    assert result.is_valid

def test_bad_total_fails():
    invoice = valid_invoice()
    invoice["total"] = 999.0
    result = validate_invoice(invoice)
    assert not result.is_valid
    assert any("subtotal + tax" in e for e in result.errors)

def test_low_confidence_fails():
    invoice = valid_invoice()
    invoice["confidence"]["invoice_number"] = 0.20
    result = validate_invoice(invoice, confidence_threshold=0.70)
    assert not result.is_valid
    assert "invoice_number" in result.low_confidence_fields

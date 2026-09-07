from __future__ import annotations

from dataclasses import dataclass, asdict
from math import isclose


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    low_confidence_fields: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _sum_line_amounts(invoice: dict) -> tuple[float, int, int]:
    total = 0.0
    calculable = 0
    items = invoice.get("line_items", [])
    for item in items:
        amount = item.get("amount")
        if amount is None:
            qty = item.get("quantity")
            unit_price = item.get("unit_price")
            if qty is not None and unit_price is not None:
                amount = qty * unit_price
        if amount is not None:
            total += float(amount)
            calculable += 1
    return total, calculable, len(items)


def validate_invoice(invoice: dict, confidence_threshold: float = 0.70, tolerance: float = 0.05) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    low_confidence_fields: list[str] = []

    if not invoice.get("invoice_number"):
        errors.append("invoice_number is required")

    total = invoice.get("total")
    if total is None or float(total) <= 0:
        errors.append("total must be greater than 0")

    subtotal = invoice.get("subtotal")
    tax = invoice.get("tax")
    line_sum, calculable_lines, total_lines = _sum_line_amounts(invoice)

    if subtotal is not None and total_lines > 0:
        if calculable_lines == total_lines:
            if not isclose(line_sum, float(subtotal), abs_tol=tolerance):
                errors.append(
                    f"line-item amount sum ({line_sum:.2f}) does not match subtotal ({float(subtotal):.2f}) within tolerance {tolerance}"
                )
        else:
            warnings.append(
                f"Line reconciliation skipped: only {calculable_lines}/{total_lines} line amounts were calculable"
            )

    if subtotal is not None and tax is not None and total is not None:
        expected_total = float(subtotal) + float(tax)
        if not isclose(expected_total, float(total), abs_tol=tolerance):
            errors.append(
                f"subtotal + tax ({expected_total:.2f}) does not match total ({float(total):.2f}) within tolerance {tolerance}"
            )

    critical_fields = ["invoice_number", "invoice_date", "supplier_name", "subtotal", "total"]
    confidence = invoice.get("confidence", {})
    for field_name in critical_fields:
        score = confidence.get(field_name)
        if score is None:
            warnings.append(f"No confidence score returned for critical field: {field_name}")
            continue
        if float(score) < confidence_threshold:
            low_confidence_fields.append(field_name)

    if low_confidence_fields:
        errors.append(
            "critical fields below confidence threshold "
            f"{confidence_threshold}: {', '.join(low_confidence_fields)}"
        )

    if not invoice.get("line_items"):
        warnings.append("No line items extracted")

    return ValidationResult(
        is_valid=not errors,
        errors=errors,
        warnings=warnings,
        low_confidence_fields=low_confidence_fields,
    )

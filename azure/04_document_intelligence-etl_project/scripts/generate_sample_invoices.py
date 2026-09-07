from __future__ import annotations

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

OUT_DIR = Path(__file__).resolve().parents[1] / "samples" / "input"

INVOICES = [
    {
        "name": "invoice_001.pdf", "id": "SYN-2026-001", "date": "2026-08-20",
        "vendor": "Contoso Office Supplies Pvt Ltd", "customer": "Fabrikam Analytics Pvt Ltd",
        "items": [("A4 Paper Box", 2, 1200.00), ("Printer Toner", 1, 2500.00)], "tax_rate": 0.18,
    },
    {
        "name": "invoice_002.pdf", "id": "SYN-2026-002", "date": "2026-08-21",
        "vendor": "Northwind IT Services", "customer": "Adventure Works Research",
        "items": [("Cloud Support Hours", 4, 1500.00), ("Data Backup Service", 1, 2000.00)], "tax_rate": 0.18,
    },
    {
        "name": "invoice_003.pdf", "id": "SYN-2026-003", "date": "2026-08-22",
        "vendor": "Blue Yonder Hardware", "customer": "Tailspin Toys Labs",
        "items": [("USB-C Dock", 2, 4500.00), ("Keyboard", 3, 1800.00)], "tax_rate": 0.18,
    },
    {
        "name": "invoice_004.pdf", "id": "SYN-2026-004", "date": "2026-08-23",
        "vendor": "Wingtip Logistics", "customer": "Woodgrove Data Services",
        "items": [("Courier Service", 5, 650.00), ("Packaging Material", 10, 120.00)], "tax_rate": 0.18,
    },
    {
        "name": "invoice_005.pdf", "id": "SYN-2026-005", "date": "2026-08-24",
        "vendor": "Proseware Training", "customer": "Lucerne Publishing",
        "items": [("Azure Workshop Seat", 2, 6000.00), ("Lab Credits", 2, 1000.00)], "tax_rate": 0.18,
    },
    {
        "name": "invoice_006_malformed.pdf", "id": "", "date": "2026-08-25",
        "vendor": "Synthetic Error Vendor", "customer": "Synthetic Test Customer",
        "items": [("Test Item A", 1, 1000.00), ("Test Item B", 1, 500.00)], "tax_rate": 0.18,
        "force_total": 9999.00,
    },
]


def money(v: float) -> str:
    return f"INR {v:,.2f}"


def create_invoice(cfg: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / cfg["name"]
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("SYNTHETIC INVOICE - FOR AZURE POC ONLY", styles["Title"]), Spacer(1, 5*mm)]
    story.append(Paragraph(f"Vendor Name: {cfg['vendor']}", styles["Normal"]))
    story.append(Paragraph("Vendor Address: 100 Fictional Tech Park, Hyderabad, India", styles["Normal"]))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(f"Invoice ID: {cfg['id'] or '[MISSING ON PURPOSE]'}", styles["Normal"]))
    story.append(Paragraph(f"Invoice Date: {cfg['date']}", styles["Normal"]))
    story.append(Paragraph(f"Customer Name: {cfg['customer']}", styles["Normal"]))
    story.append(Paragraph("Customer Address: 200 Sample Avenue, Hyderabad, India", styles["Normal"]))
    story.append(Spacer(1, 6*mm))

    rows = [["Description", "Quantity", "Unit Price", "Amount"]]
    subtotal = 0.0
    for desc, qty, unit_price in cfg["items"]:
        amount = qty * unit_price
        subtotal += amount
        rows.append([desc, str(qty), money(unit_price), money(amount)])

    table = Table(rows, colWidths=[80*mm, 25*mm, 35*mm, 35*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 7),
        ("TOPPADDING", (0,0), (-1,0), 7),
    ]))
    story.append(table)
    story.append(Spacer(1, 6*mm))

    tax = round(subtotal * cfg["tax_rate"], 2)
    total = cfg.get("force_total", round(subtotal + tax, 2))
    totals = Table([
        ["Sub Total", money(subtotal)],
        ["Total Tax", money(tax)],
        ["Invoice Total", money(total)],
        ["Currency", "INR"],
    ], colWidths=[120*mm, 55*mm])
    totals.setStyle(TableStyle([
        ("ALIGN", (1,0), (1,-1), "RIGHT"),
        ("FONTNAME", (0,2), (-1,2), "Helvetica-Bold"),
        ("LINEABOVE", (0,2), (-1,2), 0.8, colors.black),
    ]))
    story.append(totals)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("This document is fictional and contains no real financial or personal data.", styles["Italic"]))
    doc.build(story)
    print(f"Created {path}")


if __name__ == "__main__":
    for invoice in INVOICES:
        create_invoice(invoice)

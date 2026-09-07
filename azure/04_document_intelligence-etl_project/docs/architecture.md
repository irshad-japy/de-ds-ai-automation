# Architecture

```text
Synthetic invoice PDFs
       |
       v
ADLS Gen2 / Blob container: documents
  incoming/
       |
       v
Python batch runner OR Azure Function Blob Trigger
       |
       v
Azure AI Document Intelligence (prebuilt-invoice)
       |
       +--> processed/raw/*.raw.json   (audit/debug)
       |
       v
Stable normalized invoice schema
       |
       v
Validation
  - invoice number required
  - total > 0
  - line sum ~= subtotal
  - subtotal + tax ~= total
  - confidence threshold
       |
   +---+---+
   |       |
 valid   invalid/low confidence
   |       |
   v       v
Azure SQL  failed/*.failure.json
header + line
   |
   v
processed/*.json
```

## Why local batch first?

A beginner can separate problems: first prove Document Intelligence, Storage, validation and SQL. Only after that works, add the Function trigger. This makes troubleshooting much easier.

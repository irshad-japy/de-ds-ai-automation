pytest -q

pytest -v tests/conftest.py
pytest -v tests/test_format.py
pytest -v tests/test_qdrant_data_helper.py
pytest -v tests/

setx TAVILY_API_KEY "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"
$env:WEB_FALLBACK = "yes"
$env:TAVILY_API_KEY="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"
$env:PYTHONPATH = (Get-Location).Path

# run mcp server
mcp dev mcp_server/server.py

is this good idea i wanted to store rag query resopnse in kb??
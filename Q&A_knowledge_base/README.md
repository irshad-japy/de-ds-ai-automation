# 0) ensure qdrant and (optionally) ollama are running via your docker compose
#    qdrant:  localhost:6333
#    ollama:  localhost:11434   (pull the models you set in .env)

# 1) setup
poetry env use python3.12
poetry install
cp .env.example .env
# edit .env to set PROVIDER=ollama or openrouter and desired models

# 2) ingest your local folder
# put files into ./input then:
$env:PYTHONPATH = "src"
poetry run python scripts/ingest.py --folder .\input
poetry run uvicorn lr.api.main:app --reload --host 0.0.0.0 --port 8080

# 3) start API
poetry run uvicorn lr.api.main:app --reload --port 8080

4) ingest docs in qdrant
$json = @'
{
  "folder": "input"
}
'@
$res = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/ingest" -ContentType "application/json" -Body $json
$res | ConvertTo-Json -Depth 10

# 4) ask
$json = @'
{ "query": "Which ports must I open in the AWS EC2 security group for RustDesk?" }
'@
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/ask" -ContentType "application/json" -Body $json

-----------------------------------------------------------
ask full quesion ad get answer using  below command

# 1) Capture the response
$json = @'
{ "query": "Which ports must I open in the AWS EC2 security group for RustDesk?" }
'@
$res = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/ask" -ContentType "application/json" -Body $json

# 2) View the full answer only (no truncation)
$res.answer

# or dump the whole object fully expanded
$res | ConvertTo-Json -Depth 10

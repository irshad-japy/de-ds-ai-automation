# run it (step‑by‑step)
## create project & install

git init ai-agent-poc && cd ai-agent-poc
# add files above
python -m venv .venv && . .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env   # fill your tokens

# ingest KB
python -m src.app ingest --pdf-dir data/raw --url-file urls.jsonl

# ask KB questions
python -m src.app ask "Summarize the Glue ETL pipeline decisions"

# Jira → code → Draft MR
python -m src.app jira2mr "https://your.atlassian.net/browse/PROJ-123" "git@gitlab.com:yourgroup/yourrepo.git" --target-branch main
# → prints {"issue":"PROJ-123","plan":"...","files_count":N,"mr_url":"https://gitlab.com/.../merge_requests/..." }


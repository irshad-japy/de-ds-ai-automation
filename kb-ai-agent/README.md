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
python -m src.app ask "give me Summarize"

# Jira → code → Draft MR
# In your repo root where src/app.py lives
python -m src.app jira2mr "https://teamglobalexp.atlassian.net/browse/MYT-41273" "https://gitlab.com/teamglobalexp/mytoll/myteamge-glue-a2asubscription-processor-milestone.git" --target-branch main


# → prints {"issue":"PROJ-123","plan":"...","files_count":N,"mr_url":"https://gitlab.com/.../merge_requests/..." }

----------------------------------------------------
# 1️⃣ Activate your Poetry environment
cd kb-ai-agent
poetry shell

# 2️⃣ (First time only) Ingest your knowledge base
poetry run python -m src.app ingest --pdf-dir data/raw --url-file urls.jsonl

# 3️⃣ Ask KB questions
poetry run python -m src.app ask "Summarize the Glue ETL pipeline decisions"

poetry run python -m src.app ask "give me Summarize"
poetry run python -m src.app jira2mr "https://teamglobalexp.atlassian.net//browse/PROJ-123" "https://gitlab.com/teamglobalexp/mytoll/myteamge-glue-common-utils.git" --target-branch main


# 4️⃣ Run Jira → code → Draft MR flow
poetry run python -m src.app jira "https://your.atlassian.net/browse/PROJ-123"

Start Chroma:
docker-compose up -d
docker-compose down

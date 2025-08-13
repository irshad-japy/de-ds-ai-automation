import os, re, requests

BASE = os.getenv("JIRA_BASE_URL")
TOKEN = os.getenv("JIRA_TOKEN")

def issue_key_from_url(url: str) -> str:
    m = re.search(r"/browse/([A-Z][A-Z0-9]+-\d+)", url)
    if not m:
        raise ValueError("Could not parse Jira issue key from URL.")
    return m.group(1)

def get_issue(key: str):
    r = requests.get(
        f"{BASE}/rest/api/3/issue/{key}",
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}
    )
    r.raise_for_status()
    j = r.json()
    title = j["fields"]["summary"]
    desc  = j["fields"].get("description")
    return {"key": key, "title": title, "description": str(desc)}

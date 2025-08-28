"""
python -m src.tools.jira_client
"""

# src/tools/jira_client.py
from __future__ import annotations

import os
import re
import requests
from typing import Dict, Any


def issue_key_from_url(jira_url: str) -> str:
    m = re.search(r"/([A-Z0-9]+-\d+)(?:[/?#]|$)", jira_url)
    if not m:
        raise ValueError(f"Cannot parse issue key from: {jira_url}")
    return m.group(1)


def _flatten_adf(node):
    # Naive ADF (Atlassian Document Format) -> plain text
    if isinstance(node, dict):
        t = node.get("type")
        if t == "text":
            return node.get("text", "")
        txt = ""
        for c in node.get("content", []) or []:
            txt += _flatten_adf(c)
        if t in {"paragraph", "heading"}:
            txt += "\n"
        return txt
    if isinstance(node, list):
        return "".join(_flatten_adf(x) for x in node)
    return ""


def get_issue(issue_key: str) -> Dict[str, Any]:
    base = os.getenv("JIRA_BASE_URL", "").rstrip("/")
    email = os.getenv("JIRA_USER_EMAIL", "")
    token = os.getenv("JIRA_API_TOKEN", "")
    if not (base and email and token):
        raise RuntimeError("Missing Jira env: JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN")

    url = f"{base}/rest/api/3/issue/{issue_key}"
    r = requests.get(url, auth=(email, token), headers={"Accept": "application/json"})
    if r.status_code >= 400:
        raise RuntimeError(f"Jira fetch failed {r.status_code}: {r.text[:400]}")
    data = r.json()
    fields = data.get("fields", {})

    summary = fields.get("summary") or ""
    desc_raw = fields.get("description")
    if isinstance(desc_raw, dict):  # ADF
        description = _flatten_adf(desc_raw).strip()
    else:
        description = (desc_raw or "").strip()

    # crude AC extraction from description
    ac = ""
    import re as _re
    m = _re.search(r"(acceptance\s*criteria|ac)[:\s]+([\s\S]+)", description, _re.IGNORECASE)
    if m:
        ac = m.group(2).strip()

    return {
        "key": issue_key,
        "title": summary,
        "description": description,
        "acceptance_criteria": ac,
        "status": (fields.get("status") or {}).get("name"),
        "assignee": (fields.get("assignee") or {}).get("displayName"),
        "reporter": (fields.get("reporter") or {}).get("displayName"),
        "raw": data,
    }


if __name__ == "__main__":
    key = issue_key_from_url("jira_url")
    issue = get_issue(key)  # -> {"key","title","description","acceptance_criteria","status","assignee","reporter"}
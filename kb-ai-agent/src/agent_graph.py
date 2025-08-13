from typing import Dict
from .tools.kb_search import search_kb
from .tools.coder import propose_code_change
from .tools.jira_client import issue_key_from_url, get_issue
from .tools.gitlab_client import create_branch_commit_push, open_draft_mr

def jira_to_mr_flow(jira_url: str, repo_url: str, target_branch="main") -> Dict:
    key = issue_key_from_url(jira_url)
    issue = get_issue(key)
    # 1) search KB for context
    kb = search_kb(f"{key} {issue['title']}")
    # 2) ask coder to propose files
    plan = propose_code_change(spec=f"{issue['title']}\n\n{issue['description']}", kb_snippets=kb)
    branch = f"auto/{key}"
    # 3) apply edits & push
    files = {f["path"]: f["content"] for f in plan.get("files", [])}
    if files:
        create_branch_commit_push(repo_url, branch, files)
        mr_url = open_draft_mr(branch, f"{key}: {issue['title']}", plan.get("plan",""), target_branch=target_branch)
    else:
        mr_url = None
    return {"issue": key, "plan": plan.get("plan",""), "mr_url": mr_url, "files_count": len(files)}

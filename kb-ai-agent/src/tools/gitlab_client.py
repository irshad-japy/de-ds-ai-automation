# src/tools/gitlab_client.py
from __future__ import annotations

import os
import shlex
import json
import tempfile
import subprocess
from urllib.parse import urlparse, quote_plus
from typing import Dict, Optional, Tuple

import requests


def _run(cmd: str, cwd: Optional[str] = None) -> Tuple[int, str, str]:
    p = subprocess.Popen(
        shlex.split(cmd), cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    out, err = p.communicate()
    return p.returncode, out.strip(), err.strip()


def _git_config_identity(cwd: str) -> None:
    user = os.getenv("GIT_USERNAME", "Automation Bot")
    email = os.getenv("GIT_EMAIL", "automation@example.com")
    _run(f'git config user.name "{user}"', cwd=cwd)
    _run(f'git config user.email "{email}"', cwd=cwd)


def create_branch_commit_push(repo_url: str, branch: str, files: Dict[str, str]) -> None:
    """
    Clone (shallow), create branch, write files dict[path]=content, commit & push.
    """
    tmp = tempfile.mkdtemp(prefix="jira2mr_")
    code, out, err = _run(f"git clone --depth 1 {shlex.quote(repo_url)} .", cwd=tmp)
    if code != 0:
        raise RuntimeError(f"git clone failed: {err or out}")
    _git_config_identity(tmp)

    code, out, err = _run(f"git checkout -b {shlex.quote(branch)}", cwd=tmp)
    if code != 0:
        raise RuntimeError(f"git checkout -b failed: {err or out}")

    # write files
    for path, content in files.items():
        full = os.path.join(tmp, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    code, out, err = _run("git add -A", cwd=tmp)
    if code != 0:
        raise RuntimeError(f"git add failed: {err or out}")

    msg = f"chore: apply jira2mr changes ({branch})"
    code, out, err = _run(f'git commit -m "{msg}"', cwd=tmp)
    if code != 0:
        raise RuntimeError(f"git commit failed: {err or out}")

    code, out, err = _run(f"git push -u origin {shlex.quote(branch)}", cwd=tmp)
    if code != 0:
        raise RuntimeError(f"git push failed: {err or out}")


def open_draft_mr(source_branch: str, title: str, description: str, target_branch: str = "main") -> str:
    """
    Create a DRAFT/WIP MR on GitLab for the current repo_url remote.
    We need the project path; infer from `git remote get-url origin`.
    """
    token = os.getenv("GITLAB_TOKEN", "")
    if not token:
        raise RuntimeError("GITLAB_TOKEN is required")

    # Infer the remote origin URL to detect host/project
    code, out, err = _run("git remote get-url origin")
    if code != 0:
        raise RuntimeError(f"git remote get-url origin failed: {err or out}")
    repo_url = out.strip()

    parsed = urlparse(repo_url)
    path = parsed.path.rstrip(".git").lstrip("/")
    api_base = f"{parsed.scheme}://{parsed.netloc}/api/v4"

    # Project lookup
    proj = requests.get(
        f"{api_base}/projects/{quote_plus(path)}",
        headers={"PRIVATE-TOKEN": token},
    )
    if proj.status_code >= 400:
        raise RuntimeError(f"GitLab project lookup failed: {proj.status_code} {proj.text[:200]}")
    pid = proj.json()["id"]

    payload = {
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": f"Draft: {title}" if not title.lower().startswith("draft:") else title,
        "description": description or "",
        "remove_source_branch": True,
        "squash": False,
    }
    mr = requests.post(
        f"{api_base}/projects/{pid}/merge_requests",
        headers={"PRIVATE-TOKEN": token, "Content-Type": "application/json"},
        data=json.dumps(payload),
    )
    if mr.status_code >= 400:
        raise RuntimeError(f"GitLab MR create failed: {mr.status_code} {mr.text[:200]}")
    return mr.json().get("web_url")

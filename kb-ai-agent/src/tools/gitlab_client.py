import os, subprocess, tempfile
import requests, textwrap

GL = os.getenv("GL_BASE_URL", "https://gitlab.com")
GL_TOKEN = os.getenv("GL_TOKEN")
PROJECT_ID = os.getenv("GL_PROJECT_ID")

def create_branch_commit_push(repo_url: str, branch: str, file_edits: dict):
    """
    file_edits: {relative_path: new_text}
    """
    with tempfile.TemporaryDirectory() as d:
        subprocess.check_call(["git", "clone", repo_url, d])
        subprocess.check_call(["git", "-C", d, "checkout", "-b", branch])

        for rel, content in file_edits.items():
            p = os.path.join(d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
        subprocess.check_call(["git", "-C", d, "add", "."])
        subprocess.check_call(["git", "-C", d, "commit", "-m", f"{branch}: automated change"])
        subprocess.check_call(["git", "-C", d, "push", "origin", branch])

def open_draft_mr(source_branch: str, title: str, description: str, target_branch="main"):
    r = requests.post(
        f"{GL}/api/v4/projects/{PROJECT_ID}/merge_requests",
        headers={"PRIVATE-TOKEN": GL_TOKEN},
        data={
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": f"Draft: {title}",
            "description": textwrap.dedent(description)
        }
    )
    r.raise_for_status()
    return r.json()["web_url"]

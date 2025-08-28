import os, glob, json, click
from dotenv import load_dotenv
from .tools.kb_ingest import ingest_pdfs, ingest_text_blobs
from .tools.kb_search import search_kb
from .agent_graph import jira_to_mr_flow

load_dotenv()

@click.group()
def cli(): ...

@cli.command("ingest")
@click.option("--pdf-dir", default="./data/raw", help="Folder with PDFs")
@click.option("--url-file", default=None, help="Optional JSONL with {'text','source'} items")
def ingest(pdf_dir, url_file):
    pdfs = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    if pdfs:
        click.echo(f"Ingesting {len(pdfs)} PDFs...")
        ingest_pdfs(pdfs)
    if url_file and os.path.isfile(url_file):
        items = [json.loads(l) for l in open(url_file, "r", encoding="utf-8").read().splitlines() if l.strip()]
        click.echo(f"Ingesting {len(items)} text/url items...")
        ingest_text_blobs(items)
    click.echo("✅ Ingest complete.")

@cli.command("ask")
@click.argument("question")
@click.option("--k", default=5)
def ask(question, k):
    hits = search_kb(question, k=k)
    for i,(doc,meta) in enumerate(hits,1):
        click.echo(f"\n[{i}] {meta['source']}\n{doc[:600]}...")

@cli.command("jira2mr")
@click.argument("jira_url")
@click.argument("repo_url")
@click.option("--target-branch", default="main")
def jira2mr(jira_url, repo_url, target_branch):
    out = jira_to_mr_flow(jira_url, repo_url, target_branch)
    click.echo(json.dumps(out, indent=2))

if __name__ == "__main__":
    cli()

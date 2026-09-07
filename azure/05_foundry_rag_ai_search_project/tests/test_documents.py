from pathlib import Path
from rag.documents import parse_markdown_document


def test_parse_frontmatter(tmp_path: Path):
    p = tmp_path / "doc.md"
    p.write_text(
        "---\ntitle: Demo\nsource: demo.md\ncategory: policy\n---\nHello world",
        encoding="utf-8",
    )
    doc = parse_markdown_document(p)
    assert doc.title == "Demo"
    assert doc.source == "demo.md"
    assert doc.category == "policy"
    assert doc.content == "Hello world"

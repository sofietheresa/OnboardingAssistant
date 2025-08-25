from pathlib import Path
from typing import Iterable, Dict
import re

def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def read_pdf(path: Path) -> str:
    import pypdf
    reader = pypdf.PdfReader(str(path))
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)

def read_docx(path: Path) -> str:
    import docx
    doc = docx.Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)

LOADERS = {
    ".md": read_markdown,
    ".markdown": read_markdown,
    ".pdf": read_pdf,
    ".docx": read_docx,
}

def load_documents(paths: Iterable[Path]) -> Iterable[Dict]:
    """
    Liest unterstützte Dateien ein und liefert Dicts mit doc_id, text, metadata.
    """
    for p in paths:
        ext = p.suffix.lower()
        if ext in LOADERS:
            text = LOADERS[ext](p)
            text = re.sub(r"[ \t]+", " ", text).strip()
            yield {
                "doc_id": p.name,
                "text": text,
                "metadata": {"filename": p.name, "path": str(p), "source": "file"},
            }

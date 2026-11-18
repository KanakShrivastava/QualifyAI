from pathlib import Path
import fitz
from docx import Document

def _read_pdf(path: str) -> str:
    text_parts = []
    with fitz.open(path) as pdf:
        for page_num, page in enumerate(pdf, start=1):
            page_text = page.get_text("text")
            if page_text.strip():
                text_parts.append(f"[Page {page_num}]\n{page_text}")
    return "\n\n".join(text_parts)

def _read_docx(path: str) -> str:
    doc = Document(path)
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))
    return "\n".join(parts)

def load_resume(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(file_path)
    if suffix == ".docx":
        return _read_docx(file_path)
    raise ValueError("Resume must be a PDF or DOCX file.")

def load_job_description(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(file_path)
    if suffix == ".txt":
        return Path(file_path).read_text(encoding="utf-8", errors="replace")
    raise ValueError("Job description must be a PDF or TXT file.")

from pathlib import Path

from .docx_parser import extract_docx
from .pdf_parser import extract_pdf
from .xlsx_parser import extract_xlsx


def extract_text(path: Path) -> str:
    """Dispatch on file extension. Returns extracted text or raises ValueError."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(path)
    if suffix in (".docx", ".doc"):
        return extract_docx(path)
    if suffix in (".xlsx", ".xls"):
        return extract_xlsx(path)
    if suffix in (".txt", ".md", ".csv", ".json"):
        return path.read_text(encoding="utf-8", errors="replace")
    raise ValueError(f"Unsupported file type: {suffix}")

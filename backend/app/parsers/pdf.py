from io import BytesIO

from pypdf import PdfReader


def parse_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or '' for page in reader.pages]
    return '\n'.join(page.strip() for page in pages if page.strip())
from io import BytesIO

from docx import Document


def parse_docx(content: bytes) -> str:
    document = Document(BytesIO(content))
    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]
    return '\n'.join(paragraphs)
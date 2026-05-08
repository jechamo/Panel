import json
from pathlib import Path
from uuid import uuid4

from app.core.settings import get_settings
from app.models.file import UploadedFileReference
from app.parsers.docx import parse_docx
from app.parsers.pdf import parse_pdf
from app.parsers.xlsx import parse_xlsx


class FileStorageError(Exception):
    pass


SUPPORTED_EXTENSIONS = {
    '.docx': parse_docx,
    '.pdf': parse_pdf,
    '.xlsx': parse_xlsx,
}


def store_uploaded_file(
    flow_id: str,
    filename: str,
    content_type: str,
    content: bytes,
) -> UploadedFileReference:
    extension = Path(filename).suffix.lower()
    parser = SUPPORTED_EXTENSIONS.get(extension)

    if parser is None:
        raise FileStorageError(
            'Only .docx, .xlsx and .pdf attachments are supported in this phase.',
        )

    file_id = str(uuid4())
    variable_name = Path(filename).stem
    upload_dir = get_uploads_storage_path() / flow_id / file_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f'source{extension}'
    parsed_text = parser(content)

    (upload_dir / stored_name).write_bytes(content)
    (upload_dir / 'parsed.txt').write_text(parsed_text, encoding='utf-8')
    (upload_dir / 'metadata.json').write_text(
        json.dumps(
            {
                'id': file_id,
                'flowId': flow_id,
                'mimeType': content_type or 'application/octet-stream',
                'name': filename,
                'storedName': stored_name,
                'variableName': variable_name,
            },
            indent=2,
        ),
        encoding='utf-8',
    )

    return UploadedFileReference(
        id=file_id,
        flowId=flow_id,
        mimeType=content_type or 'application/octet-stream',
        name=filename,
        storedName=stored_name,
        variableName=variable_name,
    )


def get_uploads_storage_path() -> Path:
    storage_path = Path(get_settings().uploads_storage_dir)
    if not storage_path.is_absolute():
        storage_path = Path(__file__).resolve().parents[2] / storage_path

    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path
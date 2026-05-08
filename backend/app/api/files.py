import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..db import UPLOADS_DIR

router = APIRouter(prefix="/api/files", tags=["files"])

_ALLOWED = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".md", ".csv", ".json"}


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if suffix not in _ALLOWED:
        raise HTTPException(400, f"Unsupported extension: {suffix}")

    rel = f"{uuid.uuid4().hex}{suffix}"
    dest = UPLOADS_DIR / rel
    contents = await file.read()
    dest.write_bytes(contents)

    return {
        "name": file.filename,
        "path": rel,
        "size": len(contents),
    }


@router.delete("/{path}")
def delete_file(path: str):
    safe = (UPLOADS_DIR / path).resolve()
    try:
        safe.relative_to(UPLOADS_DIR.resolve())
    except ValueError:
        raise HTTPException(400, "Invalid path") from None
    if safe.exists():
        safe.unlink()
    return {"ok": True}

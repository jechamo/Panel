from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.file_storage import FileStorageError, store_uploaded_file
from app.core.responses import error_response, success_response

router = APIRouter(prefix='/files', tags=['files'])


@router.post('/upload', status_code=status.HTTP_201_CREATED)
async def upload_file(flow_id: str = Form(...), file: UploadFile = File(...)):
    if not flow_id.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(
                'missing_flow_id',
                'A saved flow id is required before uploading files.',
            ),
        )

    content = await file.read()

    try:
        uploaded_file = store_uploaded_file(
            flow_id,
            file.filename or 'upload.bin',
            file.content_type or '',
            content,
        )
    except FileStorageError as error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response('file_upload_error', str(error)),
        )

    return success_response(uploaded_file.model_dump(mode='json'))
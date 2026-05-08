from pydantic import BaseModel


class UploadedFileReference(BaseModel):
    id: str
    flowId: str
    mimeType: str
    name: str
    storedName: str
    variableName: str
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class NodeRunLog(BaseModel):
    id: str
    flowId: str | None = None
    nodeId: str
    nodeKind: Literal['agent', 'microservice']
    status: Literal['success', 'error']
    startedAt: datetime
    finishedAt: datetime
    input: Any = None
    output: Any = None
    error: str | None = None
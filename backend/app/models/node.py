from typing import Any, Literal

from pydantic import BaseModel


class HeaderItem(BaseModel):
    id: str
    key: str
    value: str


class MicroserviceNodeConfig(BaseModel):
    endpoint: str
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    headers: list[HeaderItem]
    payload: str


class NodeRunRequest(BaseModel):
    kind: Literal['microservice']
    config: MicroserviceNodeConfig


class NodeRunResult(BaseModel):
    output: Any
    status_code: int
from typing import Any, Literal

from pydantic import BaseModel


class FlowBase(BaseModel):
    name: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    version: Literal[1] = 1


class FlowCreateRequest(FlowBase):
    pass


class FlowUpdateRequest(FlowBase):
    id: str


class FlowDocument(FlowBase):
    id: str


class FlowSummary(BaseModel):
    id: str
    name: str
    version: Literal[1]
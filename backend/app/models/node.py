from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class HeaderItem(BaseModel):
    id: str
    key: str
    value: str


class MicroserviceNodeConfig(BaseModel):
    endpoint: str
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    headers: list[HeaderItem]
    payload: str


class AgentNodeConfig(BaseModel):
    systemPrompt: str
    userPrompt: str
    model: str


class MicroserviceNodeRunRequest(BaseModel):
    kind: Literal['microservice']
    config: MicroserviceNodeConfig


class AgentNodeRunRequest(BaseModel):
    kind: Literal['agent']
    config: AgentNodeConfig


NodeRunRequest = Annotated[
    AgentNodeRunRequest | MicroserviceNodeRunRequest,
    Field(discriminator='kind'),
]


class NodeRunResult(BaseModel):
    output: Any
    status_code: int
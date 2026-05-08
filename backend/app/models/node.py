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
    outputFields: list['OutputFieldItem']
    systemPrompt: str
    userPrompt: str
    model: str


class OutputFieldItem(BaseModel):
    id: str
    name: str
    description: str


class NodeExecutionContext(BaseModel):
    flowId: str | None = None
    input: Any = None


class MicroserviceNodeRunRequest(BaseModel):
    kind: Literal['microservice']
    config: MicroserviceNodeConfig
    context: NodeExecutionContext = Field(default_factory=NodeExecutionContext)


class AgentNodeRunRequest(BaseModel):
    kind: Literal['agent']
    config: AgentNodeConfig
    context: NodeExecutionContext = Field(default_factory=NodeExecutionContext)


NodeRunRequest = Annotated[
    AgentNodeRunRequest | MicroserviceNodeRunRequest,
    Field(discriminator='kind'),
]


class NodeRunResult(BaseModel):
    output: Any
    status_code: int
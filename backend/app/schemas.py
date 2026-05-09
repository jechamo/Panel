from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FlowSummary(BaseModel):
    id: int
    name: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class FlowDetail(FlowSummary):
    graph: dict[str, Any]


class FlowCreate(BaseModel):
    name: str
    graph: dict[str, Any] = Field(default_factory=dict)


class FlowUpdate(BaseModel):
    name: str | None = None
    graph: dict[str, Any] | None = None


class SettingItem(BaseModel):
    key: str
    value: str


class SettingsView(BaseModel):
    """What the UI sees: keys present, values masked."""

    anthropic_api_key: bool = False
    openai_api_key: bool = False
    gemini_api_key: bool = False
    github_token: bool = False
    present: dict[str, bool] = Field(default_factory=dict)


class RunRequest(BaseModel):
    graph: dict[str, Any]
    node_id: str | None = None  # if set: run that single node


class NodeOutput(BaseModel):
    node_id: str
    status: str  # "ok" | "error" | "skipped"
    output: Any = None
    error: str | None = None
    duration_ms: int = 0


class RunResponse(BaseModel):
    results: list[NodeOutput]

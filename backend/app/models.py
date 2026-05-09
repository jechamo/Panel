from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Flow(Base):
    __tablename__ = "flows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    graph: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Setting(Base):
    """Encrypted key/value store for provider credentials."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value_encrypted: Mapped[bytes] = mapped_column(default=b"")


class NodeRun(Base):
    """One row per node execution. Used for audit and the UI run history."""

    __tablename__ = "node_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    flow_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    node_id: Mapped[str] = mapped_column(String(120), index=True)
    node_kind: Mapped[str] = mapped_column(String(32))  # 'agent' | 'microservice'
    status: Mapped[str] = mapped_column(String(16))  # 'ok' | 'error' | 'skipped'
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    input_json: Mapped[str] = mapped_column(Text, default="")
    output_json: Mapped[str] = mapped_column(Text, default="")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

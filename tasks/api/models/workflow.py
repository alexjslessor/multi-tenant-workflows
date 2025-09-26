from typing import Any, Literal
from uuid import uuid4
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from .base import Base

class WorkflowModel(Base):
    __tablename__ = "workflow"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    workflow: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

class WorkflowResultModel(Base):
    __tablename__ = "workflow_result"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    workflow_result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

class WorkflowJson(BaseModel):
    action: Literal["http_request", 'summarize_text', 'save_to_database']
    params: dict[str, Any] | None = None

class WorkflowSchemaBase(BaseModel):
    tenant_id: str
    workflow: list[WorkflowJson]
    model_config = ConfigDict(from_attributes=True)

class WorkflowSchema(WorkflowSchemaBase):
    id: str = Field(default_factory=lambda: str(uuid4()))


# WORKFLOW RESULT
class WorkflowResultSchemaBase(BaseModel):
    workflow_id: str
    workflow_result: list[dict[str, Any]]
    model_config = ConfigDict(from_attributes=True)

class WorkflowResultSchema(WorkflowResultSchemaBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
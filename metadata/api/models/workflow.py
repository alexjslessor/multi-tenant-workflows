from decimal import Decimal

from sqlalchemy import Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class MetadataExecution(Base):
    __tablename__ = "metadata_execution"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    workflow_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    execution_count: Mapped[int] = mapped_column(Integer, nullable=False)
    execution_time_avg: Mapped[Decimal] = mapped_column(Numeric, nullable=False)

import logging
from sqlalchemy.future import select
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_async_session
from api_lib.lib import FrontendException
from ..models.workflow import (
    WorkflowSchema,
    WorkflowModel,
    WorkflowResultModel,
)
from .pagination import pagination
from ..lib.rabbit import broadcast_message
from .rabbit_conn import get_channel

logger = logging.getLogger("uvicorn")

async def create_workflow(
    workflow: WorkflowSchema,
    channel = Depends(get_channel),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        data = workflow.model_dump()
        record = WorkflowModel(**data)
        db.add(record)
        await db.commit()

        await broadcast_message(
            channel,
            {
                "id": record.id,
                "tenant_id": record.tenant_id,
                "workflow": workflow.workflow,
            },
            "create_workflow",
        )
        return record
    except Exception as e:
        await db.rollback()
        logger.error(e)
        raise FrontendException(
            status_code=500,
            detail="Failed to create workflow",
            error=str(e),
            color="error",
        )

async def list_workflow(
    pages: tuple[int, int] = Depends(pagination),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        skip, limit = pages
        query = select(WorkflowModel).offset(skip).limit(limit)
        result = await db.execute(query)
        resp = result.scalars().all()
        return resp
    except Exception as e:
        logger.error(e)
        raise FrontendException(
            status_code=500,
            detail="Failed to list workflows",
            error=str(e),
            color="error",
        )

async def list_workflow_results(
    # tenant_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        query = select(
            WorkflowResultModel
        )#.where(WorkflowResultModel.tenant_id == tenant_id)
        result = await db.execute(query)
        resp = result.scalars().all()
        return resp
    except Exception as e:
        logger.error(e)
        raise FrontendException(
            status_code=500,
            detail="Failed to list workflow results",
            error=str(e),
            color="error",
        )

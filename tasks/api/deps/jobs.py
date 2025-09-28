import logging
from fastapi import Depends
from celery.result import AsyncResult as CeleryAsyncResult

from api_lib.lib import FrontendException

from ..tasks import celery, execute_workflow
from ..lib.rabbit import broadcast_message
from .db import redis_client, get_channel
from ..settings import get_settings

settings = get_settings()
logger = logging.getLogger("tasks")

async def trigger_workflow(
    id: str,
    channel = Depends(get_channel),
):
    try:
        task = execute_workflow.delay(
            id,
        )
        await broadcast_message(
            channel,
            {
                "workflow_id": id, 
                "job_id": task.id,
            },
            "trigger_workflow",
        )
        return {
            "job_id": task.id,
        }
    except Exception as e:
        logger.error(e)
        raise FrontendException(
            status_code=500,
            detail="Failed to start workflow",
            error=str(e),
            color="error",
        )

async def get_job_status(
    job_id: str,
):
    """Get the status of a celery background job by job_id

    Args:
        job_id (str): uuidv4 string.

    Returns:
        dict: job_id, state, status, result
    """
    task = CeleryAsyncResult(job_id, app=celery)
    return {
        "job_id": job_id,
        "state": task.state,
        "status": task.status,
        "result": task.result if task.ready() else None
    }

def list_jobs(
    redis_client = Depends(redis_client),
):
    """get all job ids and statuses from redis cache"""
    try:
        redis_keys = redis_client.keys("celery-task-meta-*")
        results = []
        for job_key in redis_keys:
            job_id = job_key.decode().replace("celery-task-meta-", "")
            task = CeleryAsyncResult(job_id, app=celery)
            result = {
                "job_id": job_id,
                "state": task.state,
                "status": task.status,
            }
            results.append(result)
        return results
    except Exception as e:
        logger.error(e)
        raise FrontendException(
            status_code=500, 
            detail="Error fetching job statuses", 
            error="Server Error", 
            color="error"
        )

# async def get_workflow_job_result(
#     tenant_id: str,
#     job_id: str,
# ):
#     try:
#         task = CeleryAsyncResult(job_id, app=celery)
#         if task.ready():
#             res = task.result
#             # Optional: ensure tenant_id matches in result
#             if isinstance(res, dict) and res.get("tenant_id") == tenant_id:
#                 return WorkflowJobResult(result=res)
#             return WorkflowJobResult(result=res if isinstance(res, dict) else {"value": res})
#         return WorkflowJobResult(result=None)
#     except Exception as e:
#         logger.error(e)
#         raise FrontendException(
#             status_code=404,
#             detail="Job not found",
#             error=str(e),
#             color="error",
#         )
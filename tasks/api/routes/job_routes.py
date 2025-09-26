from fastapi import APIRouter, Depends
from ..settings import get_settings
from ..models import (
    JobOut,
)
from ..deps.jobs import (
    trigger_workflow,
    get_job_status,
    list_jobs,
)

settings = get_settings()
router = APIRouter()


@router.post(
    "/job/workflow-trigger/{id}",
)
async def start_workflow_or_404(
    resp = Depends(trigger_workflow),
):
    """Start a Celery task to execute a workflow by ID for a tenant.
    Body: { tenant_id, workflow_id }
    Returns: { job_id }
    """
    return resp

@router.get(
    "/job/status/{job_id}",
    response_model=JobOut,
)
async def get_job_or_404(
    resp = Depends(get_job_status),
):
    return resp

@router.get(
    "/job/list",
    response_model=list[JobOut],
)
async def list_jobs_or_404(
    resp = Depends(list_jobs),
):
    return resp
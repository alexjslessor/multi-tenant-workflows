from fastapi import APIRouter, Depends
from ..settings import get_settings
from ..deps.workflow import (
    create_workflow,
    list_workflow,
)
from ..models.workflow import (
    WorkflowSchema,
)

settings = get_settings()
router = APIRouter()

@router.post(
    "/workflow-create",
    response_model=WorkflowSchema,
)
async def workflow_create_or_404(
    resp = Depends(create_workflow),
):
    """Create a new workflow.
    Body: { tenant_id, workflow_definition }
    Returns: { status, result }
    """
    return resp

@router.get(
    "/workflow-list",
    response_model=list[WorkflowSchema],
)
async def workflow_list_or_404(
    resp = Depends(list_workflow),
):
    """Returns a list of workflows.
    """
    return resp
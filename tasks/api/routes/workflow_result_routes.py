from fastapi import APIRouter, Depends
from ..settings import get_settings
from ..deps.workflow import (
    list_workflow_results,
)
from ..models.workflow import (
    WorkflowResultSchema,
)

settings = get_settings()
router = APIRouter()

@router.get(
    "/workflow-result-list",
    response_model=list[WorkflowResultSchema],
)
async def workflow_results_list_or_404(
    resp = Depends(list_workflow_results),
):
    """Returns a list of workflow results.
    """
    return resp
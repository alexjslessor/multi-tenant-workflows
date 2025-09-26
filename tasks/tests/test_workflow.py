import pytest
import logging
from api.models.workflow import (
    WorkflowModel, 
    WorkflowResultModel,
    WorkflowSchema,
    WorkflowSchemaBase,
    WorkflowJson,
)

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.asyncio

@pytest.mark.workflow_create_route
class TestCreateWorkflow:

    async def test_create_workflow(
        self, 
        dummy_workflow,
        test_client, 
    ):
        body = WorkflowSchema(
            tenant_id="tenant-1",
            workflow=dummy_workflow,
        )
        resp = await test_client.post("/workflow-create", json=body.model_dump())
        assert resp.status_code == 200, f'{resp.status_code} - {resp.json()}'

        data = resp.json()
        print(data)
        assert isinstance(data.get("id"), str) and len(data["id"]) > 0
        assert data["tenant_id"] == body.tenant_id
        print(data['workflow'])

@pytest.mark.workflow_list_route
class TestListWorkflow:

    async def test_list_workflow(
        self, 
        test_client,
    ):
        resp = await test_client.get("/workflow-list")
        assert resp.status_code == 200, \
            f'{resp.status_code} - {resp.json()}'
        data = resp.json()
        print(data)

@pytest.mark.workflow_result_list_route
class TestListWorkflowResults:

    async def test_list_workflow_results(
        self, 
        test_client,
    ):
        resp = await test_client.get("/workflow-result-list")
        assert resp.status_code == 200, f'{resp.status_code} - {resp.json()}'
        data = resp.json()
        print(data)
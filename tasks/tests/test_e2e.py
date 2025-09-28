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

class TestE2E:

    @pytest.mark.e2e_create_workflow
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
        return data['id']

    @pytest.mark.e2e_job_start
    async def test_job_start(
        self,
        dummy_workflow,
        test_client,
    ):
        # create a new workflow and get the id
        id = await self.test_create_workflow(dummy_workflow, test_client)
        # trigger a job with the new workflows id
        job_resp = await test_client.post(
            f"/job/workflow-trigger/{id}",
        )
        assert job_resp.status_code == 200, \
            f"{job_resp.status_code} - {job_resp.json()}"
        print(job_resp.json())

    @pytest.mark.e2e
    async def test_job_e2e(self, dummy_workflow, test_client):
        # create a new workflow and get the id
        id = await self.test_create_workflow(dummy_workflow, test_client)

        # trigger a job with the new workflows id
        job_resp = await test_client.post(
            f"/job/workflow-trigger/{id}"
        )
        assert job_resp.status_code == 200, \
            f"{job_resp.status_code} - {job_resp.json()}"

        # get the job_id 
        job_id = job_resp.json()['job_id']
        job_status_resp = await test_client.get(
            f"/job/status/{job_id}",
        )
        assert job_status_resp.status_code == 200, \
            f"{job_status_resp.status_code} - {job_status_resp.json()}"

        print(job_status_resp.json())

        job_list_resp = await test_client.get(
            f"/job/list"
        )
        assert job_list_resp.status_code == 200, \
            f"{job_list_resp.status_code} - {job_list_resp.json()}"
        print(job_list_resp.json())

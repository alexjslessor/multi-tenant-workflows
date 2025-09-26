import pytest
import logging
from api.main import app
from api.deps.jobs import (
    trigger_workflow,
    get_job_status, 
    list_jobs, 
)

logger = logging.getLogger('uvicorn')
pytestmark = pytest.mark.asyncio

async def override_trigger_workflow(id: str):
    assert isinstance(id, str) and id
    return {
        "job_id": "job-123",
    }

async def override_get_job_status(job_id: str):
    assert isinstance(job_id, str) and job_id
    return {
        "job_id": job_id,
        "state": "SUCCESS",
        "status": "SUCCESS",
        "result": [],
    }

async def override_list_jobs():
    return [
        {
            "job_id": "job-1", 
            "state": "PENDING", 
            "status": "PENDING",
        },
        {
            "job_id": "job-2", 
            "state": "SUCCESS", 
            "status": "SUCCESS",
        },
    ]

@pytest.mark.job_start
class TestJobStart:

    async def test_job_start(self, test_client):
        app.dependency_overrides[trigger_workflow] = override_trigger_workflow
        try:
            workflow_id = "wf-1"
            resp = await test_client.post(f"/job/workflow-trigger/{workflow_id}")
            assert resp.status_code == 200, f"{resp.status_code} - {resp.text}"
            assert resp.json() == {"job_id": "job-123"}
        finally:
            app.dependency_overrides.clear()

@pytest.mark.job_status
class TestJobStatus:

    async def test_job_status_response_validation(self, test_client):
        app.dependency_overrides[get_job_status] = override_get_job_status
        try:
            job_id = "job-xyz"
            resp = await test_client.get(f"/job/status/{job_id}")
            assert resp.status_code == 200, f"{resp.status_code} - {resp.text}"
            print(resp.json())
            assert resp.json() == {
                "job_id": job_id,
                "state": "SUCCESS",
                "status": "SUCCESS",
                "result": [],
            }
        finally:
            app.dependency_overrides.clear()

@pytest.mark.job_list
class TestJobList:

    async def test_job_list_response_validation(
        self, 
        test_client,
    ):
        app.dependency_overrides[list_jobs] = override_list_jobs
        try:
            resp = await test_client.get("/job/list")
            print(resp.json())
            assert resp.status_code == 200, f"{resp.status_code} - {resp.json()}"
            assert resp.json() == [
                {
                    "job_id": "job-1", 
                    "state": "PENDING", 
                    "status": "PENDING",
                    'result': [],
                },
                {
                    "job_id": "job-2", 
                    "state": "SUCCESS", 
                    "status": "SUCCESS",
                    'result': [],
                },
            ]
        finally:
            app.dependency_overrides.clear()
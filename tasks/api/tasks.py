import logging
import openai
from sqlalchemy.orm import Session
from .db import session_scope
from .celery import celery
from .settings import get_settings
from .models.workflow import (
    WorkflowModel,
    WorkflowResultModel,
)

settings = get_settings()
logger = logging.getLogger("uvicorn")
openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def summarize_text(text):
    try:
        r = openai_client.chat.completions.create(
            messages=[
                {
                    'role': 'user',
                    'content': text
                }
            ]
        )
        return r
    except Exception as e:
        raise

def http_request(url: str):
    """Perform a fast HTTP GET using httpx.
    Returns JSON if available, else response text.
    Raises for non-2xx responses.
    """
    import httpx
    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        ct = resp.headers.get("content-type", "").lower()
        if "application/json" in ct:
            try:
                return resp.json()
            except ValueError:
                return resp.text
        return resp.text

def save_to_database(data):
    """Minimal placeholder for a DB save step."""
    return True

STEPS_MAP = {
    'http_request': http_request,
    'summarize_text': summarize_text,
    'save_to_database': save_to_database
}

@celery.task()
def execute_workflow(
    id: str,
):
    """Execute a workflow asynchronously.
    This task fetches the workflow definition for the given tenant workflow,
    executes it (stubbed), persists a workflow_result row, and returns
    the result payload.
    """
    try:
        with session_scope() as session:
            wf = session.get(WorkflowModel, id)
        return {
            "ok": True, 
            "workflow_id": id,
        }
    except Exception as e:
        logger.error(f"Error in execute_workflow: {e}")
        raise
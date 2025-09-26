from pydantic import BaseModel, Field

class JobOutBase(BaseModel):
    job_id: str = Field(
        ..., 
        description='The job ID')
    state: str = Field(
        ..., 
        description='The state of the job')
    status: str = Field(
        ..., 
        description='The status of the job')

class JobOut(JobOutBase):
    result: list | None = Field(
        default_factory=lambda: [], 
        description='The result of the job')
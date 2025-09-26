import enum

# Enum for Job Status
class JobStatusEnum(str, enum.Enum):
    """Celery job statuses"""
    STARTED = 'STARTED'
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
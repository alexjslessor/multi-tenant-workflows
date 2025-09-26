import pytest
from types import SimpleNamespace

from api.tasks import execute_workflow, celery


@pytest.fixture(autouse=True)
def eager_tasks():
    """Run Celery tasks eagerly for unit testing."""
    celery.conf.task_always_eager = True
    celery.conf.task_eager_propagates = True
    yield


class FakeSession:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.committed = False
        self.rolled_back = False
        self.closed = False
        self.get_calls = []

    def get(self, model, id_):
        self.get_calls.append((model, id_))
        if self.should_fail:
            raise RuntimeError("db fail")
        return SimpleNamespace(id=id_)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def _patch_session_scope(monkeypatch, fake_session: FakeSession):
    import api.tasks as tasks_mod

    class FakeCtx:
        def __enter__(self):
            return fake_session

        def __exit__(self, exc_type, exc, tb):
            if exc_type is None:
                fake_session.commit()
            else:
                fake_session.rollback()
            fake_session.close()
            return False

    monkeypatch.setattr(tasks_mod, "session_scope", lambda: FakeCtx())


class TestCeleryTask:
    def test_execute_workflow_success(self, monkeypatch):
        fake = FakeSession()
        _patch_session_scope(monkeypatch, fake)

        res = execute_workflow.delay("wf-123").get()
        assert res == {"ok": True, "workflow_id": "wf-123"}
        assert fake.committed is True
        assert fake.rolled_back is False
        assert fake.closed is True
        assert fake.get_calls and fake.get_calls[0][1] == "wf-123"

    def test_execute_workflow_failure(self, monkeypatch):
        fake = FakeSession(should_fail=True)
        _patch_session_scope(monkeypatch, fake)

        with pytest.raises(RuntimeError, match="db fail"):
            execute_workflow.delay("wf-err").get()
        assert fake.committed is False
        assert fake.rolled_back is True
        assert fake.closed is True
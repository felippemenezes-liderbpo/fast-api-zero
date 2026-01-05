from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import User, table_registry


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def mock_db_time():
    @contextmanager
    def _factory(model: type, time: datetime = datetime(2026, 1, 1)):
        def fake_time_hook(target, **_):
            if hasattr(target, 'created_at'):
                target.created_at = time
            if hasattr(target, 'updated_at'):
                target.updated_at = time

        event.listen(model, 'before_insert', fake_time_hook, named=True)
        event.listen(model, 'before_update', fake_time_hook, named=True)
        try:
            yield time
        finally:
            event.remove(model, 'before_insert', fake_time_hook)
            event.remove(model, 'before_update', fake_time_hook)

    return _factory


@pytest.fixture
def user(session):
    user = User(username='test', email='test@test.com', password='testtest')
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

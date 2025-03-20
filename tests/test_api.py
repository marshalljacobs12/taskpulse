import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.services.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.task import Base

# Test database setup
TEST_DATABASE_URL = "postgresql://taskpulse:secret@localhost:5432/taskpulse_db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_task(setup_database):
    response = client.post(
        "/tasks/",
        json={"type": "test_task", "params": {"data": "example"}}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "test_task"
    assert data["params"] == {"data": "example"}
    assert data["status"] == "pending"
    assert data["retries"] == 0
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)

def test_get_task(setup_database):
    # Create a task first
    create_response = client.post(
        "/tasks/",
        json={"type": "test_task", "params": {"data": "example"}}
    )
    task_id = create_response.json()["id"]

    # Get the task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["type"] == "test_task"

def test_get_task_not_found(setup_database):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
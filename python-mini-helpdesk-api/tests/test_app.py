import pytest
from app import app, init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        init_db()
        yield client


def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Mini Help Desk API" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_create_task(client):
    payload = {
        "title": "Fix login bug",
        "description": "Password reset issue",
        "status": "Open",
        "priority": "High",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Fix login bug"


def test_list_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Test task",
            "description": "Example",
            "status": "Open",
            "priority": "Medium",
        },
    )
    task_id = create_response.get_json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Test task"


def test_update_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Test task",
            "description": "Example",
            "status": "Open",
            "priority": "Medium",
        },
    )
    task_id = create_response.get_json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
            "status": "In Progress",
            "priority": "High",
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["title"] == "Updated title"


def test_delete_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Delete me",
            "description": "Remove later",
            "status": "Open",
            "priority": "Low",
        },
    )
    task_id = create_response.get_json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert "deleted" in response.get_json()["message"].lower()

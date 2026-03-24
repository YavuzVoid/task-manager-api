import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_task_manager.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def get_token():
    client.post("/auth/register", json={"username": "test", "email": "test@test.com", "password": "test123"})
    resp = client.post("/auth/login", json={"username": "test", "password": "test123"})
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login():
    resp = client.post("/auth/register", json={"username": "user1", "email": "u1@test.com", "password": "pass123"})
    assert resp.status_code == 201
    resp = client.post("/auth/login", json={"username": "user1", "password": "pass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_duplicate_register():
    client.post("/auth/register", json={"username": "dup", "email": "dup@test.com", "password": "pass123"})
    resp = client.post("/auth/register", json={"username": "dup", "email": "dup2@test.com", "password": "pass123"})
    assert resp.status_code == 400


def test_create_project():
    token = get_token()
    resp = client.post("/projects/", json={"name": "İş", "description": "İş görevleri"}, headers=auth(token))
    assert resp.status_code == 201
    assert resp.json()["name"] == "İş"


def test_create_task():
    token = get_token()
    resp = client.post("/tasks/", json={"title": "Test görevi", "priority": "high"}, headers=auth(token))
    assert resp.status_code == 201
    assert resp.json()["priority"] == "high"
    assert resp.json()["status"] == "todo"


def test_create_task_with_project():
    token = get_token()
    proj = client.post("/projects/", json={"name": "Proje1"}, headers=auth(token)).json()
    resp = client.post("/tasks/", json={"title": "Proje görevi", "project_id": proj["id"]}, headers=auth(token))
    assert resp.status_code == 201
    assert resp.json()["project_id"] == proj["id"]


def test_filter_tasks_by_status():
    token = get_token()
    client.post("/tasks/", json={"title": "Todo", "status": "todo"}, headers=auth(token))
    client.post("/tasks/", json={"title": "Done", "status": "done"}, headers=auth(token))
    resp = client.get("/tasks/?status=done", headers=auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Done"


def test_filter_tasks_by_priority():
    token = get_token()
    client.post("/tasks/", json={"title": "Low task", "priority": "low"}, headers=auth(token))
    client.post("/tasks/", json={"title": "High task", "priority": "high"}, headers=auth(token))
    resp = client.get("/tasks/?priority=high", headers=auth(token))
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "High task"


def test_search_tasks():
    token = get_token()
    client.post("/tasks/", json={"title": "Alışveriş yap"}, headers=auth(token))
    client.post("/tasks/", json={"title": "Kod yaz"}, headers=auth(token))
    resp = client.get("/tasks/?search=alışveriş", headers=auth(token))
    assert len(resp.json()) == 1


def test_update_task():
    token = get_token()
    task = client.post("/tasks/", json={"title": "Eski"}, headers=auth(token)).json()
    resp = client.put(f"/tasks/{task['id']}", json={"title": "Yeni", "status": "done"}, headers=auth(token))
    assert resp.status_code == 200
    assert resp.json()["title"] == "Yeni"
    assert resp.json()["status"] == "done"


def test_delete_task():
    token = get_token()
    task = client.post("/tasks/", json={"title": "Silinecek"}, headers=auth(token)).json()
    resp = client.delete(f"/tasks/{task['id']}", headers=auth(token))
    assert resp.status_code == 204
    resp = client.get(f"/tasks/{task['id']}", headers=auth(token))
    assert resp.status_code == 404


def test_unauthorized_access():
    resp = client.get("/tasks/")
    assert resp.status_code == 401


def test_user_isolation():
    client.post("/auth/register", json={"username": "a", "email": "a@t.com", "password": "p"})
    t1 = client.post("/auth/login", json={"username": "a", "password": "p"}).json()["access_token"]
    client.post("/auth/register", json={"username": "b", "email": "b@t.com", "password": "p"})
    t2 = client.post("/auth/login", json={"username": "b", "password": "p"}).json()["access_token"]
    client.post("/tasks/", json={"title": "A görevi"}, headers=auth(t1))
    resp = client.get("/tasks/", headers=auth(t2))
    assert len(resp.json()) == 0

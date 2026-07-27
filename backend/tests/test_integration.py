import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.dependencies import get_storage_provider, get_quota_service
from app.main import app
from app.models.user import User
from app.models.project import Project
from app.models.upload import Upload
from app.modules.uploads.quota import QuotaService
from app.storage.local import LocalStorageProvider


@pytest.fixture
def _engine(tmp_path):
    db_path = str(tmp_path / "test.db")
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def _SessionLocal(_engine):
    return sessionmaker(bind=_engine, autoflush=False)


@pytest.fixture
def tmp_upload_root():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def seed_user(_SessionLocal):
    session = _SessionLocal()
    user = User(email="seed@example.com", password_hash="hash", name="Seed User")
    session.add(user)
    session.commit()
    user_id = user.id
    session.close()
    return user_id


@pytest.fixture
def auth_token(seed_user):
    from app.core.security import create_access_token
    return create_access_token({"sub": str(seed_user)})


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def client(_SessionLocal, tmp_upload_root):
    def _override_get_db():
        db = _SessionLocal()
        try:
            yield db
        finally:
            db.close()

    provider = LocalStorageProvider(root=tmp_upload_root)

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_storage_provider] = lambda: provider
    app.dependency_overrides[get_quota_service] = lambda: QuotaService(type("Settings", (), {
        "MAX_PROJECT_STORAGE_GB": 5,
    })())

    yield TestClient(app)

    app.dependency_overrides.clear()


class TestAuth:
    def test_register(self, client):
        resp = client.post("/auth/register", json={
            "email": "new@example.com",
            "password": "password123",
            "name": "New User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "password" not in data

    def test_register_duplicate_email(self, client):
        client.post("/auth/register", json={
            "email": "dup@example.com",
            "password": "password123",
            "name": "First",
        })
        resp = client.post("/auth/register", json={
            "email": "dup@example.com",
            "password": "password123",
            "name": "Second",
        })
        assert resp.status_code == 409
        assert resp.json()["detail"]["code"] == "EMAIL_EXISTS"

    def test_login_success(self, client):
        client.post("/auth/register", json={
            "email": "login@example.com",
            "password": "password123",
            "name": "Login User",
        })
        resp = client.post("/auth/login", json={
            "email": "login@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client):
        client.post("/auth/register", json={
            "email": "fail@example.com",
            "password": "password123",
            "name": "Fail User",
        })
        resp = client.post("/auth/login", json={
            "email": "fail@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401

    def test_me_authenticated(self, client, auth_headers):
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "seed@example.com"

    def test_me_unauthenticated(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401


class TestProjects:
    def test_create_project(self, client, auth_headers):
        resp = client.post("/projects", json={"name": "My Project"}, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My Project"
        assert data["status"] == "pending"

    def test_create_project_with_description(self, client, auth_headers):
        resp = client.post("/projects", json={
            "name": "Desc Project",
            "description": "A project with description",
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["description"] == "A project with description"

    def test_list_projects_empty(self, client, auth_headers):
        resp = client.get("/projects", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_projects_paginated(self, client, auth_headers):
        for i in range(5):
            client.post("/projects", json={"name": f"Project {i}"}, headers=auth_headers)
        resp = client.get("/projects?page=1&size=2", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["pages"] == 3

    def test_get_project(self, client, auth_headers):
        create_resp = client.post("/projects", json={"name": "Get Me"}, headers=auth_headers)
        project_id = create_resp.json()["id"]
        resp = client.get(f"/projects/{project_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Me"

    def test_get_project_not_found(self, client, auth_headers):
        resp = client.get("/projects/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_other_users_project(self, client, auth_headers, _SessionLocal, seed_user):
        session = _SessionLocal()
        other_project = Project(user_id=seed_user + 999, name="Other's Project")
        session.add(other_project)
        session.commit()
        other_id = other_project.id
        session.close()
        resp = client.get(f"/projects/{other_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_project(self, client, auth_headers):
        create_resp = client.post("/projects", json={"name": "Original"}, headers=auth_headers)
        project_id = create_resp.json()["id"]
        resp = client.patch(f"/projects/{project_id}", json={"name": "Updated"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    def test_update_project_no_fields(self, client, auth_headers):
        create_resp = client.post("/projects", json={"name": "No Update"}, headers=auth_headers)
        project_id = create_resp.json()["id"]
        resp = client.patch(f"/projects/{project_id}", json={}, headers=auth_headers)
        assert resp.status_code == 400

    def test_delete_project(self, client, auth_headers):
        create_resp = client.post("/projects", json={"name": "Delete Me"}, headers=auth_headers)
        project_id = create_resp.json()["id"]
        resp = client.delete(f"/projects/{project_id}", headers=auth_headers)
        assert resp.status_code == 204

    def test_delete_project_not_found(self, client, auth_headers):
        resp = client.delete("/projects/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_create_project_unauthenticated(self, client):
        resp = client.post("/projects", json={"name": "Ghost"})
        assert resp.status_code == 401


class TestUploads:
    def _create_project(self, client, headers):
        resp = client.post("/projects", json={"name": "Upload Test"}, headers=headers)
        return resp.json()["id"]

    def test_upload_files(self, client, auth_headers, tmp_upload_root):
        project_id = self._create_project(client, auth_headers)
        resp = client.post(
            f"/projects/{project_id}/uploads",
            headers=auth_headers,
            files=[("files", ("test.py", b"print('hello')", "text/x-python"))],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data) == 1
        assert data[0]["original_name"] == "test.py"
        assert data[0]["file_size"] == 14

    def test_upload_multiple_files(self, client, auth_headers, tmp_upload_root):
        project_id = self._create_project(client, auth_headers)
        resp = client.post(
            f"/projects/{project_id}/uploads",
            headers=auth_headers,
            files=[
                ("files", ("a.py", b"print('a')", "text/x-python")),
                ("files", ("b.js", b"console.log('b')", "application/javascript")),
            ],
        )
        assert resp.status_code == 201
        assert len(resp.json()) == 2

    def test_upload_empty_file_rejected(self, client, auth_headers, tmp_upload_root):
        project_id = self._create_project(client, auth_headers)
        resp = client.post(
            f"/projects/{project_id}/uploads",
            headers=auth_headers,
            files=[("files", ("empty.py", b"", "text/x-python"))],
        )
        assert resp.status_code == 400
        assert resp.json()["detail"]["code"] == "EMPTY_FILE"

    def test_upload_invalid_extension(self, client, auth_headers, tmp_upload_root):
        project_id = self._create_project(client, auth_headers)
        resp = client.post(
            f"/projects/{project_id}/uploads",
            headers=auth_headers,
            files=[("files", ("evil.exe", b"boom", "application/octet-stream"))],
        )
        assert resp.status_code == 400
        assert resp.json()["detail"]["code"] == "INVALID_FILE_TYPE"

    def test_upload_no_files_rejected(self, client, auth_headers, tmp_upload_root):
        project_id = self._create_project(client, auth_headers)
        resp = client.post(
            f"/projects/{project_id}/uploads",
            headers=auth_headers,
            files=[],
        )
        assert resp.status_code == 422

    def test_upload_to_nonexistent_project(self, client, auth_headers):
        resp = client.post(
            "/projects/99999/uploads",
            headers=auth_headers,
            files=[("files", ("test.py", b"code", "text/x-python"))],
        )
        assert resp.status_code == 404

    def test_list_uploads(self, client, auth_headers, tmp_upload_root):
        project_id = self._create_project(client, auth_headers)
        client.post(
            f"/projects/{project_id}/uploads",
            headers=auth_headers,
            files=[("files", ("test.py", b"print('hello')", "text/x-python"))],
        )
        resp = client.get(f"/projects/{project_id}/uploads", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["original_name"] == "test.py"

    def test_list_uploads_pagination(self, client, auth_headers, tmp_upload_root):
        project_id = self._create_project(client, auth_headers)
        for i in range(3):
            client.post(
                f"/projects/{project_id}/uploads",
                headers=auth_headers,
                files=[("files", (f"file{i}.py", f"print({i})".encode(), "text/x-python"))],
            )
        resp = client.get(f"/projects/{project_id}/uploads?page=1&size=2", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2

    def test_get_upload(self, client, auth_headers, tmp_upload_root):
        project_id = self._create_project(client, auth_headers)
        upload_resp = client.post(
            f"/projects/{project_id}/uploads",
            headers=auth_headers,
            files=[("files", ("test.py", b"code", "text/x-python"))],
        )
        upload_id = upload_resp.json()[0]["id"]
        resp = client.get(f"/uploads/{upload_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == upload_id

    def test_delete_upload(self, client, auth_headers, tmp_upload_root):
        project_id = self._create_project(client, auth_headers)
        upload_resp = client.post(
            f"/projects/{project_id}/uploads",
            headers=auth_headers,
            files=[("files", ("test.py", b"code", "text/x-python"))],
        )
        upload_id = upload_resp.json()[0]["id"]
        resp = client.delete(f"/uploads/{upload_id}", headers=auth_headers)
        assert resp.status_code == 204
        get_resp = client.get(f"/uploads/{upload_id}", headers=auth_headers)
        assert get_resp.status_code == 404

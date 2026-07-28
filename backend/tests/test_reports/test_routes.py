from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    from app.core.dependencies import get_current_user
    from app.models.user import User
    mock_user = User(id=1, email="test@test.com", name="test")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield "mock-token"
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


class TestCreateReport:
    def test_requires_auth(self, client):
        response = client.post("/reports", json={"project_id": 1, "analysis_id": 1})
        assert response.status_code == 401

    @patch("app.modules.reports.routes.reports_service.generate_report")
    def test_returns_201(self, mock_generate, client, auth_headers):
        from datetime import datetime
        mock_generate.return_value = type("ReportResponse", (), {
            "id": 1, "project_id": 1, "analysis_id": 1, "user_id": 1,
            "title": "Analysis Report", "format": "markdown", "status": "ready",
            "content": "# Report", "file_path": None,
            "created_at": datetime(2026, 7, 28, 12, 0, 0),
            "updated_at": datetime(2026, 7, 28, 12, 0, 0),
            "model_dump": lambda: {
                "id": 1, "project_id": 1, "analysis_id": 1, "user_id": 1,
                "title": "Analysis Report", "format": "markdown", "status": "ready",
                "content": "# Report", "file_path": None,
                "created_at": "2026-07-28T12:00:00",
                "updated_at": "2026-07-28T12:00:00",
            },
        })()
        response = client.post(
            "/reports",
            json={"project_id": 1, "analysis_id": 1},
            headers=auth_headers,
        )
        assert response.status_code == 201

    def test_rejects_invalid_format(self, client, auth_headers):
        response = client.post(
            "/reports",
            json={"project_id": 1, "analysis_id": 1, "format": "pdf"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestListReports:
    def test_requires_auth(self, client):
        response = client.get("/reports?project_id=1")
        assert response.status_code == 401

    def test_requires_project_id(self, client, auth_headers):
        response = client.get("/reports", headers=auth_headers)
        assert response.status_code == 422

    @patch("app.modules.reports.routes.reports_service.list_reports")
    def test_returns_200_with_pagination(self, mock_list, client, auth_headers):
        mock_list.return_value = type("ReportListResponse", (), {
            "items": [], "total": 0, "page": 1, "size": 20, "pages": 1,
            "model_dump": lambda: {
                "items": [], "total": 0, "page": 1, "size": 20, "pages": 1,
            },
        })()
        response = client.get(
            "/reports?project_id=1",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestGetReport:
    def test_requires_auth(self, client):
        response = client.get("/reports/1")
        assert response.status_code == 401

    @patch("app.modules.reports.routes.reports_service.get_report")
    def test_returns_200(self, mock_get, client, auth_headers):
        from datetime import datetime
        mock_get.return_value = type("ReportResponse", (), {
            "id": 1, "project_id": 1, "analysis_id": 1, "user_id": 1,
            "title": "Analysis Report", "format": "markdown", "status": "ready",
            "content": "# Report", "file_path": None,
            "created_at": datetime(2026, 7, 28, 12, 0, 0),
            "updated_at": datetime(2026, 7, 28, 12, 0, 0),
            "model_dump": lambda: {
                "id": 1, "project_id": 1, "analysis_id": 1, "user_id": 1,
                "title": "Analysis Report", "format": "markdown", "status": "ready",
                "content": "# Report", "file_path": None,
                "created_at": "2026-07-28T12:00:00",
                "updated_at": "2026-07-28T12:00:00",
            },
        })()
        response = client.get("/reports/1", headers=auth_headers)
        assert response.status_code == 200


class TestDeleteReport:
    def test_requires_auth(self, client):
        response = client.delete("/reports/1")
        assert response.status_code == 401

    def test_returns_204(self, client, auth_headers):
        from app.core.exceptions import NotFoundException
        from app.modules.reports import service as reports_service
        original = app.dependency_overrides.copy()

        def mock_delete(db, user_id, report_id):
            if report_id != 1:
                raise NotFoundException("Report")

        with patch.object(reports_service, "delete_report", side_effect=mock_delete):
            response = client.delete("/reports/1", headers=auth_headers)
            assert response.status_code == 204


class TestOwnership:
    @patch("app.modules.reports.routes.reports_service.get_report")
    def test_not_found_returns_404(self, mock_get, client, auth_headers):
        from app.core.exceptions import NotFoundException
        mock_get.side_effect = NotFoundException("Report")
        response = client.get("/reports/999", headers=auth_headers)
        assert response.status_code == 404

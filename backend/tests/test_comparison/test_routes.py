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


class TestCreateComparison:
    def test_requires_auth(self, client):
        response = client.post(
            "/comparison",
            json={"project_id": 1, "analysis_a_id": 1, "analysis_b_id": 2},
        )
        assert response.status_code == 401

    @patch("app.modules.comparison.routes.comparison_service.generate_comparison")
    def test_returns_201(self, mock_generate, client, auth_headers):
        from datetime import datetime
        from app.modules.comparison.schemas import ComparisonData

        mock_generate.return_value = type("ComparisonResponse", (), {
            "id": 1, "project_id": 1, "analysis_a_id": 1, "analysis_b_id": 2,
            "summary": "Test summary",
            "comparison_data": ComparisonData(),
            "created_at": datetime(2026, 7, 28, 12, 0, 0),
            "model_dump": lambda: {
                "id": 1, "project_id": 1, "analysis_a_id": 1, "analysis_b_id": 2,
                "summary": "Test summary",
                "comparison_data": {
                    "technologies": {"added": [], "removed": [], "common": [], "version_changes": []},
                    "dependencies": {"added": [], "removed": [], "updated": []},
                    "files": {"added": [], "removed": [], "modified": [], "total_a": 0, "total_b": 0},
                    "warnings": {"added": [], "resolved": [], "persistent": [], "delta": 0},
                    "metrics": {
                        "loc": None, "file_count": None, "dependency_count": None,
                        "technology_count": None, "warning_count": None,
                    },
                },
                "created_at": "2026-07-28T12:00:00",
            },
        })()
        response = client.post(
            "/comparison",
            json={"project_id": 1, "analysis_a_id": 1, "analysis_b_id": 2},
            headers=auth_headers,
        )
        assert response.status_code == 201

    def test_requires_both_analysis_ids(self, client, auth_headers):
        response = client.post(
            "/comparison",
            json={"project_id": 1, "analysis_a_id": 1},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestGetComparison:
    def test_requires_auth(self, client):
        response = client.get("/comparison/1")
        assert response.status_code == 401

    @patch("app.modules.comparison.routes.comparison_service.get_comparison")
    def test_returns_200(self, mock_get, client, auth_headers):
        from datetime import datetime
        from app.modules.comparison.schemas import ComparisonData

        mock_get.return_value = type("ComparisonResponse", (), {
            "id": 1, "project_id": 1, "analysis_a_id": 1, "analysis_b_id": 2,
            "summary": "Test summary",
            "comparison_data": ComparisonData(),
            "created_at": datetime(2026, 7, 28, 12, 0, 0),
            "model_dump": lambda: {
                "id": 1, "project_id": 1, "analysis_a_id": 1, "analysis_b_id": 2,
                "summary": "Test summary",
                "comparison_data": None,
                "created_at": "2026-07-28T12:00:00",
            },
        })()
        response = client.get("/comparison/1", headers=auth_headers)
        assert response.status_code == 200


class TestListComparisons:
    def test_requires_auth(self, client):
        response = client.get("/comparison/project/1")
        assert response.status_code == 401

    @patch("app.modules.comparison.routes.comparison_service.list_comparisons")
    def test_returns_200_with_pagination(self, mock_list, client, auth_headers):
        mock_list.return_value = type("ComparisonListResponse", (), {
            "items": [], "total": 0, "page": 1, "size": 20, "pages": 1,
            "model_dump": lambda: {
                "items": [], "total": 0, "page": 1, "size": 20, "pages": 1,
            },
        })()
        response = client.get("/comparison/project/1", headers=auth_headers)
        assert response.status_code == 200


class TestDeleteComparison:
    def test_requires_auth(self, client):
        response = client.delete("/comparison/1")
        assert response.status_code == 401

    def test_returns_204(self, client, auth_headers):
        from app.core.exceptions import NotFoundException
        from app.modules.comparison import service as comparison_service

        def mock_delete(db, user_id, comparison_id):
            if comparison_id != 1:
                raise NotFoundException("Comparison")

        with patch.object(comparison_service, "delete_comparison", side_effect=mock_delete):
            response = client.delete("/comparison/1", headers=auth_headers)
            assert response.status_code == 204


class TestOwnership:
    @patch("app.modules.comparison.routes.comparison_service.get_comparison")
    def test_not_found_returns_404(self, mock_get, client, auth_headers):
        from app.core.exceptions import NotFoundException
        mock_get.side_effect = NotFoundException("Comparison")
        response = client.get("/comparison/999", headers=auth_headers)
        assert response.status_code == 404

from unittest.mock import create_autospec

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.ai.schemas import GenerationResponse
from app.modules.ai.service import AIService


@pytest.fixture
def mock_ai_service() -> AIService:
    service = create_autospec(AIService, instance=True)
    service.generate_summary.return_value = GenerationResponse(analysis_id=1, feature="summary", content="Summary content", model="gpt-4o-mini")
    service.generate_file_explanation.return_value = GenerationResponse(analysis_id=1, feature="file_explanation", content="File explanation", model="gpt-4o-mini")
    service.generate_module_explanation.return_value = GenerationResponse(analysis_id=1, feature="module_explanation", content="Module explanation", model="gpt-4o-mini")
    service.generate_architecture.return_value = GenerationResponse(analysis_id=1, feature="architecture", content="Architecture overview", model="gpt-4o-mini")
    service.generate_technical_debt.return_value = GenerationResponse(analysis_id=1, feature="technical_debt", content="Debt analysis", model="gpt-4o-mini")
    service.generate_modernization.return_value = GenerationResponse(analysis_id=1, feature="modernization", content="Modernization recommendations", model="gpt-4o-mini")
    return service


@pytest.fixture
def client(mock_ai_service):
    from app.core.dependencies import get_ai_service
    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service
    yield TestClient(app)
    app.dependency_overrides.clear()


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


class TestSummaryEndpoint:
    def test_returns_200(self, client, auth_headers):
        response = client.post("/ai/analysis/1/summary", headers=auth_headers)
        assert response.status_code == 200

    def test_returns_generation_response(self, client, auth_headers):
        response = client.post("/ai/analysis/1/summary", headers=auth_headers)
        data = response.json()
        assert data["analysis_id"] == 1
        assert data["feature"] == "summary"
        assert data["content"] == "Summary content"
        assert data["model"] == "gpt-4o-mini"

    def test_requires_auth(self, client):
        response = client.post("/ai/analysis/1/summary")
        assert response.status_code == 401


class TestFileExplanationEndpoint:
    def test_returns_200(self, client, auth_headers):
        response = client.post("/ai/analysis/1/file/42/explain", headers=auth_headers)
        assert response.status_code == 200

    def test_returns_file_explanation(self, client, auth_headers):
        response = client.post("/ai/analysis/1/file/42/explain", headers=auth_headers)
        data = response.json()
        assert data["feature"] == "file_explanation"
        assert data["content"] == "File explanation"

    def test_requires_auth(self, client):
        response = client.post("/ai/analysis/1/file/42/explain")
        assert response.status_code == 401


class TestModuleExplanationEndpoint:
    def test_returns_200(self, client, auth_headers):
        response = client.post("/ai/analysis/1/module", json={"module_path": "src/"}, headers=auth_headers)
        assert response.status_code == 200

    def test_returns_module_explanation(self, client, auth_headers):
        response = client.post("/ai/analysis/1/module", json={"module_path": "src/"}, headers=auth_headers)
        data = response.json()
        assert data["feature"] == "module_explanation"
        assert data["content"] == "Module explanation"

    def test_requires_module_path(self, client, auth_headers):
        response = client.post("/ai/analysis/1/module", json={}, headers=auth_headers)
        assert response.status_code == 422

    def test_requires_auth(self, client):
        response = client.post("/ai/analysis/1/module", json={"module_path": "src/"})
        assert response.status_code == 401


class TestArchitectureEndpoint:
    def test_returns_200(self, client, auth_headers):
        response = client.post("/ai/analysis/1/architecture", headers=auth_headers)
        assert response.status_code == 200

    def test_returns_architecture(self, client, auth_headers):
        response = client.post("/ai/analysis/1/architecture", headers=auth_headers)
        data = response.json()
        assert data["feature"] == "architecture"
        assert data["content"] == "Architecture overview"

    def test_requires_auth(self, client):
        response = client.post("/ai/analysis/1/architecture")
        assert response.status_code == 401


class TestTechnicalDebtEndpoint:
    def test_returns_200(self, client, auth_headers):
        response = client.post("/ai/analysis/1/technical-debt", headers=auth_headers)
        assert response.status_code == 200

    def test_returns_technical_debt(self, client, auth_headers):
        response = client.post("/ai/analysis/1/technical-debt", headers=auth_headers)
        data = response.json()
        assert data["feature"] == "technical_debt"
        assert data["content"] == "Debt analysis"

    def test_requires_auth(self, client):
        response = client.post("/ai/analysis/1/technical-debt")
        assert response.status_code == 401


class TestModernizationEndpoint:
    def test_returns_200(self, client, auth_headers):
        response = client.post("/ai/analysis/1/modernization", headers=auth_headers)
        assert response.status_code == 200

    def test_returns_modernization(self, client, auth_headers):
        response = client.post("/ai/analysis/1/modernization", headers=auth_headers)
        data = response.json()
        assert data["feature"] == "modernization"
        assert data["content"] == "Modernization recommendations"

    def test_requires_auth(self, client):
        response = client.post("/ai/analysis/1/modernization")
        assert response.status_code == 401


class TestAIServiceIntegration:
    def test_all_endpoints_invoke_correct_service_method(self, mock_ai_service, client, auth_headers):
        client.post("/ai/analysis/1/summary", headers=auth_headers)
        mock_ai_service.generate_summary.assert_called_once()

        client.post("/ai/analysis/1/file/42/explain", headers=auth_headers)
        mock_ai_service.generate_file_explanation.assert_called_once()

        client.post("/ai/analysis/1/module", json={"module_path": "src/"}, headers=auth_headers)
        mock_ai_service.generate_module_explanation.assert_called_once()

        client.post("/ai/analysis/1/architecture", headers=auth_headers)
        mock_ai_service.generate_architecture.assert_called_once()

        client.post("/ai/analysis/1/technical-debt", headers=auth_headers)
        mock_ai_service.generate_technical_debt.assert_called_once()

        client.post("/ai/analysis/1/modernization", headers=auth_headers)
        mock_ai_service.generate_modernization.assert_called_once()


class TestOwnershipViaService:
    def test_service_rejects_unowned(self, mock_ai_service, client, auth_headers):
        from app.core.exceptions import NotFoundException
        mock_ai_service.generate_summary.side_effect = NotFoundException("Analysis")
        response = client.post("/ai/analysis/999/summary", headers=auth_headers)
        assert response.status_code == 404

    def test_service_rejects_missing_file(self, mock_ai_service, client, auth_headers):
        from app.core.exceptions import NotFoundException
        mock_ai_service.generate_file_explanation.side_effect = NotFoundException("File")
        response = client.post("/ai/analysis/1/file/999/explain", headers=auth_headers)
        assert response.status_code == 404

    def test_service_rejects_missing_module(self, mock_ai_service, client, auth_headers):
        from app.core.exceptions import NotFoundException
        mock_ai_service.generate_module_explanation.side_effect = NotFoundException("Module")
        response = client.post("/ai/analysis/1/module", json={"module_path": "nonexistent/"}, headers=auth_headers)
        assert response.status_code == 404


class TestModelNameInResponse:
    def test_model_name_included(self, mock_ai_service, client, auth_headers):
        mock_ai_service.generate_summary.return_value = GenerationResponse(
            analysis_id=1, feature="summary", content="Content", model="custom-model"
        )
        response = client.post("/ai/analysis/1/summary", headers=auth_headers)
        assert response.json()["model"] == "custom-model"

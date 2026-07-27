from unittest.mock import MagicMock, create_autospec

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.core.exceptions import NotFoundException
from app.integrations.ai.provider import AIProvider
from app.models.analysis import Analysis
from app.models.analysis_file import AnalysisFile
from app.models.analysis_technology import AnalysisTechnology
from app.models.analysis_warning import AnalysisWarning
from app.models.dependency import Dependency
from app.models.metric import Metric
from app.models.project import Project
from app.models.technology import Technology
from app.models.upload import Upload
from app.models.user import User
from app.modules.ai.context_builder import ContextBuilder
from app.modules.ai.prompt_loader import PromptLoader
from app.modules.ai.schemas import GenerationResponse
from app.modules.ai.service import AIService, DefaultAIService, _validate_ownership


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture
def user(db_session: Session) -> User:
    u = User(email="test@test.com", password_hash="pw", name="test")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def other_user(db_session: Session) -> User:
    u = User(email="other@test.com", password_hash="pw", name="other")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def project(db_session: Session, user: User) -> Project:
    p = Project(user_id=user.id, name="test-project")
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def upload(db_session: Session, project: Project) -> Upload:
    u = Upload(
        project_id=project.id,
        original_name="src.zip",
        stored_name="abc.zip",
        file_path=f"{project.id}/files/abc.zip",
        file_size=1000,
        mime_type="application/zip",
        extension=".zip",
        sha256_hash="hash",
        status="UPLOADED",
    )
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def analysis(db_session: Session, upload: Upload) -> Analysis:
    a = Analysis(upload_id=upload.id, status="COMPLETED")
    db_session.add(a)
    db_session.commit()
    return a


@pytest.fixture
def mock_provider() -> MagicMock:
    provider = create_autospec(AIProvider, instance=True)
    provider.generate.return_value = "AI generated content"
    provider.model_name = "gpt-4o-mini"
    return provider


@pytest.fixture
def mock_context_builder() -> MagicMock:
    return MagicMock(spec=ContextBuilder)


@pytest.fixture
def mock_prompt_loader() -> MagicMock:
    loader = MagicMock(spec=PromptLoader)
    loader.render.return_value = "Rendered prompt"
    return loader


@pytest.fixture
def service(mock_provider, mock_context_builder, mock_prompt_loader) -> DefaultAIService:
    return DefaultAIService(
        provider=mock_provider,
        context_builder=mock_context_builder,
        prompt_loader=mock_prompt_loader,
    )


class TestAIServiceABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            AIService()


class TestOwnershipValidation:
    def test_valid_ownership(self, db_session, user, analysis):
        result = _validate_ownership(db_session, user.id, analysis.id)
        assert result is not None
        assert result.id == analysis.id

    def test_missing_analysis(self, db_session, user):
        with pytest.raises(NotFoundException, match="Analysis"):
            _validate_ownership(db_session, user.id, 99999)

    def test_unowned_analysis(self, db_session, other_user, analysis):
        with pytest.raises(NotFoundException, match="Analysis"):
            _validate_ownership(db_session, other_user.id, analysis.id)


class TestGenerateSummary:
    def test_returns_generation_response(self, service, db_session, user, analysis):
        service._context_builder.build_summary_context.return_value = MagicMock()
        response = service.generate_summary(db_session, user.id, analysis.id)
        assert isinstance(response, GenerationResponse)
        assert response.analysis_id == analysis.id
        assert response.feature == "summary"
        assert response.content == "AI generated content"
        assert response.model == "gpt-4o-mini"

    def test_calls_all_layers(self, service, db_session, user, analysis):
        service.generate_summary(db_session, user.id, analysis.id)
        service._context_builder.build_summary_context.assert_called_once()
        service._prompt_loader.render.assert_called_once()
        service._provider.generate.assert_called_once()

    def test_rejects_unowned(self, service, db_session, other_user, analysis):
        with pytest.raises(NotFoundException):
            service.generate_summary(db_session, other_user.id, analysis.id)


class TestGenerateFileExplanation:
    def test_returns_generation_response(self, service, db_session, user, analysis):
        service._context_builder.build_file_explanation_context.return_value = MagicMock()
        response = service.generate_file_explanation(db_session, user.id, analysis.id, 1)
        assert response.feature == "file_explanation"

    def test_calls_context_builder_with_file_id(self, service, db_session, user, analysis):
        service.generate_file_explanation(db_session, user.id, analysis.id, 42)
        service._context_builder.build_file_explanation_context.assert_called_once_with(db_session, analysis.id, 42)

    def test_rejects_unowned(self, service, db_session, other_user, analysis):
        with pytest.raises(NotFoundException):
            service.generate_file_explanation(db_session, other_user.id, analysis.id, 1)


class TestGenerateModuleExplanation:
    def test_returns_generation_response(self, service, db_session, user, analysis):
        service._context_builder.build_module_explanation_context.return_value = MagicMock()
        response = service.generate_module_explanation(db_session, user.id, analysis.id, "src/")
        assert response.feature == "module_explanation"

    def test_calls_context_builder_with_module_path(self, service, db_session, user, analysis):
        service.generate_module_explanation(db_session, user.id, analysis.id, "src/")
        service._context_builder.build_module_explanation_context.assert_called_once_with(db_session, analysis.id, "src/")


class TestGenerateArchitecture:
    def test_returns_generation_response(self, service, db_session, user, analysis):
        service._context_builder.build_architecture_context.return_value = MagicMock()
        response = service.generate_architecture(db_session, user.id, analysis.id)
        assert response.feature == "architecture"

    def test_calls_context_builder(self, service, db_session, user, analysis):
        service.generate_architecture(db_session, user.id, analysis.id)
        service._context_builder.build_architecture_context.assert_called_once_with(db_session, analysis.id)


class TestGenerateTechnicalDebt:
    def test_returns_generation_response(self, service, db_session, user, analysis):
        service._context_builder.build_technical_debt_context.return_value = MagicMock()
        response = service.generate_technical_debt(db_session, user.id, analysis.id)
        assert response.feature == "technical_debt"

    def test_calls_context_builder(self, service, db_session, user, analysis):
        service.generate_technical_debt(db_session, user.id, analysis.id)
        service._context_builder.build_technical_debt_context.assert_called_once_with(db_session, analysis.id)


class TestGenerateModernization:
    def test_returns_generation_response(self, service, db_session, user, analysis):
        service._context_builder.build_modernization_context.return_value = MagicMock()
        response = service.generate_modernization(db_session, user.id, analysis.id)
        assert response.feature == "modernization"

    def test_calls_context_builder(self, service, db_session, user, analysis):
        service.generate_modernization(db_session, user.id, analysis.id)
        service._context_builder.build_modernization_context.assert_called_once_with(db_session, analysis.id)


class TestProviderFailure:
    def test_provider_error_propagates(self, service, db_session, user, analysis, mock_provider):
        mock_provider.generate.side_effect = Exception("Provider unavailable")
        service._context_builder.build_summary_context.return_value = MagicMock()
        with pytest.raises(Exception, match="Provider unavailable"):
            service.generate_summary(db_session, user.id, analysis.id)


class TestPromptLoaderFailure:
    def test_missing_template_propagates(self, service, db_session, user, analysis, mock_prompt_loader):
        mock_prompt_loader.render.side_effect = FileNotFoundError("Template not found")
        service._context_builder.build_summary_context.return_value = MagicMock()
        with pytest.raises(FileNotFoundError, match="Template not found"):
            service.generate_summary(db_session, user.id, analysis.id)

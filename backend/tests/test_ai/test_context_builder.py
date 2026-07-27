import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
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
from app.modules.ai.context_builder import (
    ContextBuilder,
    SummaryContext,
    FileExplanationContext,
    ModuleExplanationContext,
    ArchitectureContext,
    TechnicalDebtContext,
    ModernizationContext,
)
from app.modules.analysis import repository


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
        stored_name="abc123.zip",
        file_path=f"{project.id}/files/abc123.zip",
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
    db_session.flush()
    return a


@pytest.fixture
def tech_python(db_session: Session) -> Technology:
    t = Technology(name="Python", category="language")
    db_session.add(t)
    db_session.flush()
    return t


@pytest.fixture
def tech_fastapi(db_session: Session) -> Technology:
    t = Technology(name="FastAPI", category="framework")
    db_session.add(t)
    db_session.flush()
    return t


@pytest.fixture
def seed_data(db_session: Session, analysis: Analysis, tech_python: Technology, tech_fastapi: Technology):
    af1 = AnalysisFile(analysis_id=analysis.id, relative_path="main.py", file_name="main.py", extension=".py", file_size=500, lines_of_code=50, language="Python", is_directory=False)
    af2 = AnalysisFile(analysis_id=analysis.id, relative_path="src/util.py", file_name="util.py", extension=".py", file_size=300, lines_of_code=30, language="Python", is_directory=False)
    af3 = AnalysisFile(analysis_id=analysis.id, relative_path="README.md", file_name="README.md", extension=".md", file_size=100, lines_of_code=0, language="Markdown", is_directory=False)
    af4 = AnalysisFile(analysis_id=analysis.id, relative_path="src", file_name="src", extension=None, file_size=0, lines_of_code=None, language=None, is_directory=True)
    db_session.add_all([af1, af2, af3, af4])

    at1 = AnalysisTechnology(analysis_id=analysis.id, technology_id=tech_python.id, evidence=".py files", confidence="high")
    at2 = AnalysisTechnology(analysis_id=analysis.id, technology_id=tech_fastapi.id, evidence="requirements.txt", confidence="medium")
    db_session.add_all([at1, at2])

    dep1 = Dependency(analysis_id=analysis.id, name="fastapi", version="0.111.0", type="library", ecosystem="pypi")
    dep2 = Dependency(analysis_id=analysis.id, name="uvicorn", version="0.30.0", type="library", ecosystem="pypi")
    db_session.add_all([dep1, dep2])

    m1 = Metric(analysis_id=analysis.id, key="project.total_files", value=3)
    m2 = Metric(analysis_id=analysis.id, key="primary_language", value_str="Python")
    db_session.add_all([m1, m2])

    w1 = AnalysisWarning(analysis_id=analysis.id, detector_name="style", message="Line too long")
    w2 = AnalysisWarning(analysis_id=analysis.id, detector_name="complexity", message="High cyclomatic complexity")
    db_session.add_all([w1, w2])

    db_session.commit()


class TestSummaryContext:
    def test_builds_context(self, db_session, analysis, seed_data):
        builder = ContextBuilder()
        ctx = builder.build_summary_context(db_session, analysis.id)
        assert isinstance(ctx, SummaryContext)
        assert ctx.total_files == 3
        assert ctx.total_directories == 1
        assert len(ctx.languages) == 2
        assert ctx.primary_language == "Python"
        assert len(ctx.technologies) == 2
        assert len(ctx.dependencies) == 2
        assert len(ctx.file_count_by_extension) > 0

    def test_raises_on_missing_analysis(self, db_session):
        builder = ContextBuilder()
        with pytest.raises(Exception):
            builder.build_summary_context(db_session, 99999)


class TestFileExplanationContext:
    def test_builds_context(self, db_session, analysis, seed_data):
        files = db_session.query(AnalysisFile).filter(AnalysisFile.analysis_id == analysis.id).all()
        target = [f for f in files if f.file_name == "main.py"][0]
        builder = ContextBuilder()
        ctx = builder.build_file_explanation_context(db_session, analysis.id, target.id)
        assert isinstance(ctx, FileExplanationContext)
        assert ctx.file_name == "main.py"
        assert ctx.language == "Python"
        assert ctx.lines_of_code == 50

    def test_raises_on_missing_file(self, db_session, analysis, seed_data):
        builder = ContextBuilder()
        with pytest.raises(Exception):
            builder.build_file_explanation_context(db_session, analysis.id, 99999)


class TestModuleExplanationContext:
    def test_builds_context_for_root(self, db_session, analysis, seed_data):
        builder = ContextBuilder()
        ctx = builder.build_module_explanation_context(db_session, analysis.id, "main.py")
        assert isinstance(ctx, ModuleExplanationContext)
        assert ctx.total_files >= 1

    def test_raises_on_missing_module(self, db_session, analysis, seed_data):
        builder = ContextBuilder()
        with pytest.raises(Exception):
            builder.build_module_explanation_context(db_session, analysis.id, "nonexistent/")


class TestArchitectureContext:
    def test_builds_context(self, db_session, analysis, seed_data):
        builder = ContextBuilder()
        ctx = builder.build_architecture_context(db_session, analysis.id)
        assert isinstance(ctx, ArchitectureContext)
        assert ctx.total_files == 3
        assert len(ctx.languages) == 2
        assert len(ctx.technologies) == 2
        assert "src" in ctx.top_level_directories


class TestTechnicalDebtContext:
    def test_builds_context(self, db_session, analysis, seed_data):
        builder = ContextBuilder()
        ctx = builder.build_technical_debt_context(db_session, analysis.id)
        assert isinstance(ctx, TechnicalDebtContext)
        assert ctx.total_files == 3
        assert ctx.total_warnings == 2
        assert len(ctx.detector_breakdown) == 2
        assert len(ctx.languages) == 2


class TestModernizationContext:
    def test_builds_context(self, db_session, analysis, seed_data):
        builder = ContextBuilder()
        ctx = builder.build_modernization_context(db_session, analysis.id)
        assert isinstance(ctx, ModernizationContext)
        assert ctx.total_files == 3
        assert ctx.total_dependencies == 2
        assert ctx.total_technologies == 2
        assert "Python" in ctx.languages

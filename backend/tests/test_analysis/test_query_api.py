import datetime
import json
import math

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.core.exceptions import NotFoundException
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
from app.modules.analysis import query_service
from app.modules.analysis.schemas import (
    AnalysisDependencyResponse,
    AnalysisFileResponse,
    AnalysisListItem,
    AnalysisMetricResponse,
    AnalysisSummaryResponse,
    AnalysisTechnologyResponse,
    AnalysisWarningResponse,
    PaginatedResponse,
)


# ─── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    yield session
    session.close()


@pytest.fixture
def user(db_session: Session) -> User:
    user = User(email="bob@test.com", password_hash="pw", name="bob")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def other_user(db_session: Session) -> User:
    user = User(email="other@test.com", password_hash="pw", name="other")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def project(db_session: Session, user: User) -> Project:
    project = Project(user_id=user.id, name="test-project")
    db_session.add(project)
    db_session.flush()
    return project


@pytest.fixture
def upload(db_session: Session, project: Project) -> Upload:
    upload = Upload(
        project_id=project.id,
        original_name="archive.zip",
        stored_name="abc.zip",
        file_path=f"{project.id}/files/abc.zip",
        file_size=100,
        mime_type="application/zip",
        extension=".zip",
        sha256_hash="abc",
    )
    db_session.add(upload)
    db_session.flush()
    return upload


def _create_analysis(
    db: Session,
    upload: Upload,
    status: str = "COMPLETED",
    error_detail: str | None = None,
    completed_at: datetime.datetime | None = None,
) -> Analysis:
    analysis = Analysis(
        upload_id=upload.id,
        status=status,
        error_detail=error_detail,
        completed_at=completed_at,
    )
    db.add(analysis)
    db.flush()
    return analysis


def _add_file(db: Session, analysis_id: int, **overrides) -> AnalysisFile:
    data = dict(
        relative_path="main.py",
        file_name="main.py",
        extension=".py",
        file_size=100,
        lines_of_code=10,
        language="Python",
        is_directory=False,
    )
    data.update(overrides)
    f = AnalysisFile(analysis_id=analysis_id, **data)
    db.add(f)
    db.flush()
    return f


def _add_technology(
    db: Session,
    analysis_id: int,
    name: str = "Python",
    category: str = "language",
    evidence: str | None = None,
    confidence: str = "high",
) -> AnalysisTechnology:
    tech = Technology(name=name, category=category)
    db.add(tech)
    db.flush()
    at = AnalysisTechnology(
        analysis_id=analysis_id,
        technology_id=tech.id,
        evidence=evidence,
        confidence=confidence,
    )
    db.add(at)
    db.flush()
    return at


def _add_dependency(
    db: Session,
    analysis_id: int,
    **overrides,
) -> Dependency:
    data = dict(
        name="requests",
        version="2.28.0",
        type="library",
        source_files=json.dumps(["requirements.txt"]),
        ecosystem="pip",
    )
    data.update(overrides)
    dep = Dependency(analysis_id=analysis_id, **data)
    db.add(dep)
    db.flush()
    return dep


def _add_metric(
    db: Session,
    analysis_id: int,
    key: str = "project.total_files",
    value: int | None = 10,
    value_str: str | None = None,
) -> Metric:
    metric = Metric(analysis_id=analysis_id, key=key, value=value, value_str=value_str)
    db.add(metric)
    db.flush()
    return metric


def _add_warning(
    db: Session,
    analysis_id: int,
    detector_name: str = "LanguageDetector",
    message: str = "Something suspicious",
) -> AnalysisWarning:
    w = AnalysisWarning(
        analysis_id=analysis_id,
        detector_name=detector_name,
        message=message,
    )
    db.add(w)
    db.flush()
    return w


# ─── Summary endpoint ───────────────────────────────────────────────


class TestAnalysisSummary:
    def test_returns_summary_response(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload, completed_at=datetime.datetime(2026, 7, 26, 12, 0, 0))
        db_session.commit()

        result = query_service.get_analysis_summary(db_session, user.id, analysis.id)

        assert isinstance(result, AnalysisSummaryResponse)
        assert result.analysis_id == analysis.id
        assert result.status == "COMPLETED"

    def test_upload_id_included(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = query_service.get_analysis_summary(db_session, user.id, analysis.id)

        assert result.upload_id == upload.id

    def test_counts_all_zero_when_empty(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = query_service.get_analysis_summary(db_session, user.id, analysis.id)

        assert result.file_count == 0
        assert result.technology_count == 0
        assert result.dependency_count == 0
        assert result.metric_count == 0
        assert result.warning_count == 0

    def test_counts_reflect_data(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id)
        _add_file(db_session, analysis.id, relative_path="utils.py", file_name="utils.py")
        _add_technology(db_session, analysis.id)
        _add_dependency(db_session, analysis.id)
        _add_metric(db_session, analysis.id)
        _add_warning(db_session, analysis.id)
        db_session.commit()

        result = query_service.get_analysis_summary(db_session, user.id, analysis.id)

        assert result.file_count == 2
        assert result.technology_count == 1
        assert result.dependency_count == 1
        assert result.metric_count == 1
        assert result.warning_count == 1

    def test_duration_ms_calculated(self, db_session: Session, user: User, upload: Upload):
        created = datetime.datetime(2026, 7, 26, 12, 0, 0)
        completed = datetime.datetime(2026, 7, 26, 12, 0, 5)
        analysis = _create_analysis(db_session, upload, completed_at=completed)
        analysis.created_at = created
        db_session.commit()

        result = query_service.get_analysis_summary(db_session, user.id, analysis.id)

        assert result.duration_ms == 5000

    def test_duration_ms_none_when_not_completed(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload, status="RUNNING", completed_at=None)
        db_session.commit()

        result = query_service.get_analysis_summary(db_session, user.id, analysis.id)

        assert result.duration_ms is None

    def test_error_detail_included(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload, status="FAILED", error_detail="Something broke")
        db_session.commit()

        result = query_service.get_analysis_summary(db_session, user.id, analysis.id)

        assert result.error_detail == "Something broke"

    def test_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException) as exc:
            query_service.get_analysis_summary(db_session, user.id, 9999)
        assert "Analysis" in str(exc.value.detail["message"])

    def test_not_owned(self, db_session: Session, other_user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        with pytest.raises(NotFoundException) as exc:
            query_service.get_analysis_summary(db_session, other_user.id, analysis.id)
        assert "Analysis" in str(exc.value.detail["message"])


# ─── Files endpoint ─────────────────────────────────────────────────


class TestAnalysisFiles:
    def test_returns_paginated_response(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id)
        db_session.commit()

        result = query_service.get_analysis_files(db_session, user.id, analysis.id)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1

    def test_returns_file_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, relative_path="src/main.py")
        db_session.commit()

        result = query_service.get_analysis_files(db_session, user.id, analysis.id)

        f = result.items[0]
        assert isinstance(f, AnalysisFileResponse)
        assert f.relative_path == "src/main.py"
        assert f.extension == ".py"
        assert f.file_size == 100

    def test_pagination(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        for i in range(5):
            _add_file(db_session, analysis.id, relative_path=f"f{i}.py", file_name=f"f{i}.py")
        db_session.commit()

        page1 = query_service.get_analysis_files(db_session, user.id, analysis.id, page=1, size=2)
        page2 = query_service.get_analysis_files(db_session, user.id, analysis.id, page=2, size=2)
        page3 = query_service.get_analysis_files(db_session, user.id, analysis.id, page=3, size=2)

        assert len(page1.items) == 2
        assert len(page2.items) == 2
        assert len(page3.items) == 1
        assert page1.total == 5
        assert page1.pages == 3
        assert page1.page == 1
        assert page1.size == 2
        assert page3.page == 3

    def test_filter_by_extension(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, extension=".py")
        _add_file(db_session, analysis.id, relative_path="f.js", file_name="f.js", extension=".js")
        db_session.commit()

        result = query_service.get_analysis_files(db_session, user.id, analysis.id, extension=".js")

        assert len(result.items) == 1
        assert result.items[0].extension == ".js"

    def test_filter_by_language(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload, completed_at=datetime.datetime(2026, 7, 26, 12, 0, 0))
        _add_file(db_session, analysis.id, language="Python")
        _add_file(db_session, analysis.id, relative_path="f.js", file_name="f.js", language="JavaScript")
        db_session.commit()

        result = query_service.get_analysis_files(db_session, user.id, analysis.id, language="Python")

        assert len(result.items) == 1

    def test_filter_by_is_directory(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, is_directory=False)
        _add_file(db_session, analysis.id, relative_path="dir", file_name="dir", is_directory=True)
        db_session.commit()

        result = query_service.get_analysis_files(db_session, user.id, analysis.id, is_directory=True)

        assert len(result.items) == 1
        assert result.items[0].is_directory is True

    def test_sort_by_file_size(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, relative_path="big.py", file_size=200)
        _add_file(db_session, analysis.id, relative_path="small.py", file_size=10)
        db_session.commit()

        result = query_service.get_analysis_files(db_session, user.id, analysis.id, sort_by="file_size", sort_dir="asc")

        assert result.items[0].file_size == 10
        assert result.items[1].file_size == 200

    def test_deterministic_default_sort(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, relative_path="z.py")
        _add_file(db_session, analysis.id, relative_path="a.py", file_name="a.py")
        db_session.commit()

        result = query_service.get_analysis_files(db_session, user.id, analysis.id)

        assert result.items[0].relative_path == "a.py"
        assert result.items[1].relative_path == "z.py"

    def test_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException):
            query_service.get_analysis_files(db_session, user.id, 9999)


# ─── Technologies endpoint ──────────────────────────────────────────


class TestAnalysisTechnologies:
    def test_returns_flat_list(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id)
        db_session.commit()

        result = query_service.get_analysis_technologies(db_session, user.id, analysis.id)

        assert isinstance(result, list)

    def test_returns_technology_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id, name="Python", category="language", confidence="high")
        db_session.commit()

        result = query_service.get_analysis_technologies(db_session, user.id, analysis.id)

        t = result[0]
        assert isinstance(t, AnalysisTechnologyResponse)
        assert t.name == "Python"
        assert t.category == "language"
        assert t.confidence == "high"

    def test_multiple_technologies(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id, name="Python", category="language")
        _add_technology(db_session, analysis.id, name="Django", category="framework")
        db_session.commit()

        result = query_service.get_analysis_technologies(db_session, user.id, analysis.id)

        assert len(result) == 2
        names = sorted(t.name for t in result)
        assert names == ["Django", "Python"]

    def test_evidence_included(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id, evidence="pyproject.toml")
        db_session.commit()

        result = query_service.get_analysis_technologies(db_session, user.id, analysis.id)

        assert result[0].evidence == "pyproject.toml"

    def test_empty(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = query_service.get_analysis_technologies(db_session, user.id, analysis.id)

        assert result == []

    def test_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException):
            query_service.get_analysis_technologies(db_session, user.id, 9999)


# ─── Dependencies endpoint ───────────────────────────────────────────


class TestAnalysisDependencies:
    def test_returns_paginated_response(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id)
        db_session.commit()

        result = query_service.get_analysis_dependencies(db_session, user.id, analysis.id)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1

    def test_returns_dependency_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, name="flask", ecosystem="pip")
        db_session.commit()

        result = query_service.get_analysis_dependencies(db_session, user.id, analysis.id)

        d = result.items[0]
        assert isinstance(d, AnalysisDependencyResponse)
        assert d.name == "flask"
        assert d.ecosystem == "pip"

    def test_source_files_parsed(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, source_files=json.dumps(["req.txt", "dev.txt"]))
        db_session.commit()

        result = query_service.get_analysis_dependencies(db_session, user.id, analysis.id)

        assert result.items[0].source_files == ["req.txt", "dev.txt"]

    def test_pagination(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        for i in range(3):
            _add_dependency(db_session, analysis.id, name=f"dep{i}")
        db_session.commit()

        result = query_service.get_analysis_dependencies(db_session, user.id, analysis.id, page=1, size=2)

        assert len(result.items) == 2
        assert result.total == 3
        assert result.pages == 2

    def test_filter_by_ecosystem(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, name="flask", ecosystem="pip")
        _add_dependency(db_session, analysis.id, name="react", ecosystem="npm")
        db_session.commit()

        result = query_service.get_analysis_dependencies(db_session, user.id, analysis.id, ecosystem="npm")

        assert len(result.items) == 1
        assert result.items[0].name == "react"

    def test_filter_by_type(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, name="pytest", type="dev")
        _add_dependency(db_session, analysis.id, name="flask", type="library")
        db_session.commit()

        result = query_service.get_analysis_dependencies(db_session, user.id, analysis.id, type="dev")

        assert len(result.items) == 1
        assert result.items[0].name == "pytest"

    def test_sort_by_ecosystem(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, name="b", ecosystem="npm")
        _add_dependency(db_session, analysis.id, name="a", ecosystem="pip")
        db_session.commit()

        result = query_service.get_analysis_dependencies(db_session, user.id, analysis.id, sort_by="name", sort_dir="asc")

        assert result.items[0].name == "a"
        assert result.items[1].name == "b"

    def test_default_sort_by_name(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, name="zoo")
        _add_dependency(db_session, analysis.id, name="alpha")
        db_session.commit()

        result = query_service.get_analysis_dependencies(db_session, user.id, analysis.id)

        assert result.items[0].name == "alpha"
        assert result.items[1].name == "zoo"

    def test_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException):
            query_service.get_analysis_dependencies(db_session, user.id, 9999)


# ─── Metrics endpoint ────────────────────────────────────────────────


class TestAnalysisMetrics:
    def test_returns_flat_list(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_metric(db_session, analysis.id)
        db_session.commit()

        result = query_service.get_analysis_metrics(db_session, user.id, analysis.id)

        assert isinstance(result, list)

    def test_returns_metric_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_metric(db_session, analysis.id, key="project.total_files", value=42)
        db_session.commit()

        result = query_service.get_analysis_metrics(db_session, user.id, analysis.id)

        m = result[0]
        assert isinstance(m, AnalysisMetricResponse)
        assert m.key == "project.total_files"
        assert m.value == 42

    def test_string_value(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_metric(db_session, analysis.id, key="languages.primary", value=None, value_str="Python")
        db_session.commit()

        result = query_service.get_analysis_metrics(db_session, user.id, analysis.id)

        assert result[0].value == "Python"

    def test_int_value_takes_precedence(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_metric(db_session, analysis.id, key="project.total_files", value=10, value_str="10")
        db_session.commit()

        result = query_service.get_analysis_metrics(db_session, user.id, analysis.id)

        assert result[0].value == 10

    def test_multiple_metrics(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_metric(db_session, analysis.id, key="files.count", value=5)
        _add_metric(db_session, analysis.id, key="deps.count", value=12)
        db_session.commit()

        result = query_service.get_analysis_metrics(db_session, user.id, analysis.id)

        assert len(result) == 2
        keys = [m.key for m in result]
        assert "deps.count" in keys
        assert "files.count" in keys

    def test_empty(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = query_service.get_analysis_metrics(db_session, user.id, analysis.id)

        assert result == []

    def test_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException):
            query_service.get_analysis_metrics(db_session, user.id, 9999)


# ─── Warnings endpoint ────────────────────────────────────────────────


class TestAnalysisWarnings:
    def test_returns_paginated_response(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_warning(db_session, analysis.id)
        db_session.commit()

        result = query_service.get_analysis_warnings(db_session, user.id, analysis.id)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1

    def test_returns_warning_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_warning(db_session, analysis.id, detector_name="LangDetect", message="Odd file found")
        db_session.commit()

        result = query_service.get_analysis_warnings(db_session, user.id, analysis.id)

        w = result.items[0]
        assert isinstance(w, AnalysisWarningResponse)
        assert w.detector_name == "LangDetect"
        assert w.message == "Odd file found"

    def test_pagination(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        for i in range(4):
            _add_warning(db_session, analysis.id, message=f"warning{i}")
        db_session.commit()

        result = query_service.get_analysis_warnings(db_session, user.id, analysis.id, page=1, size=3)

        assert len(result.items) == 3
        assert result.total == 4
        assert result.pages == 2

    def test_filter_by_detector(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_warning(db_session, analysis.id, detector_name="DetA")
        _add_warning(db_session, analysis.id, detector_name="DetB")
        db_session.commit()

        result = query_service.get_analysis_warnings(db_session, user.id, analysis.id, detector_name="DetA")

        assert len(result.items) == 1
        assert result.items[0].detector_name == "DetA"

    def test_default_sort_desc_by_created_at(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        w1 = _add_warning(db_session, analysis.id, message="first")
        w2 = _add_warning(db_session, analysis.id, message="second")
        w1.created_at = datetime.datetime(2026, 1, 1)
        w2.created_at = datetime.datetime(2026, 6, 1)
        db_session.commit()

        result = query_service.get_analysis_warnings(db_session, user.id, analysis.id)

        assert result.items[0].message == "second"
        assert result.items[1].message == "first"

    def test_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException):
            query_service.get_analysis_warnings(db_session, user.id, 9999)


# ─── Project analyses endpoint ────────────────────────────────────────


class TestProjectAnalyses:
    def test_returns_paginated_response(self, db_session: Session, user: User, project: Project, upload: Upload):
        _create_analysis(db_session, upload)
        db_session.commit()

        result = query_service.list_project_analyses(db_session, user.id, project.id)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1

    def test_returns_list_item_dtos(self, db_session: Session, user: User, project: Project, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = query_service.list_project_analyses(db_session, user.id, project.id)

        item = result.items[0]
        assert isinstance(item, AnalysisListItem)
        assert item.id == analysis.id
        assert item.upload_id == upload.id

    def test_pagination(self, db_session: Session, user: User, project: Project, upload: Upload):
        for i in range(3):
            u = Upload(
                project_id=project.id,
                original_name=f"f{i}.zip",
                stored_name=f"f{i}.zip",
                file_path=f"{project.id}/files/f{i}.zip",
                file_size=10,
                mime_type="application/zip",
                extension=".zip",
                sha256_hash=f"h{i}",
            )
            db_session.add(u)
            db_session.flush()
            _create_analysis(db_session, u)
        db_session.commit()

        result = query_service.list_project_analyses(db_session, user.id, project.id, page=1, size=2)

        assert len(result.items) == 2
        assert result.total == 3
        assert result.pages == 2

    def test_default_sort_by_created_at_desc(self, db_session: Session, user: User, project: Project, upload: Upload):
        a1 = _create_analysis(db_session, upload)
        u2 = Upload(
            project_id=project.id,
            original_name="f2.zip", stored_name="f2.zip",
            file_path="f2.zip", file_size=10,
            mime_type="application/zip", extension=".zip", sha256_hash="h2",
        )
        db_session.add(u2)
        db_session.flush()
        a2 = _create_analysis(db_session, u2)
        a1.created_at = datetime.datetime(2026, 1, 1)
        a2.created_at = datetime.datetime(2026, 6, 1)
        db_session.commit()

        result = query_service.list_project_analyses(db_session, user.id, project.id)

        assert result.items[0].id == a2.id
        assert result.items[1].id == a1.id

    def test_project_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException) as exc:
            query_service.list_project_analyses(db_session, user.id, 9999)
        assert "Project" in str(exc.value.detail["message"])

    def test_project_not_owned(self, db_session: Session, other_user: User, project: Project):
        with pytest.raises(NotFoundException):
            query_service.list_project_analyses(db_session, other_user.id, project.id)

    def test_empty_project(self, db_session: Session, user: User, project: Project):
        result = query_service.list_project_analyses(db_session, user.id, project.id)

        assert len(result.items) == 0
        assert result.total == 0


# ─── Upload analyses endpoint ────────────────────────────────────────


class TestUploadAnalyses:
    def test_returns_paginated_response(self, db_session: Session, user: User, upload: Upload):
        _create_analysis(db_session, upload)
        db_session.commit()

        result = query_service.list_upload_analyses(db_session, user.id, upload.id)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1

    def test_returns_list_item_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = query_service.list_upload_analyses(db_session, user.id, upload.id)

        item = result.items[0]
        assert isinstance(item, AnalysisListItem)
        assert item.id == analysis.id
        assert item.status == "COMPLETED"

    def test_multiple_analyses(self, db_session: Session, user: User, upload: Upload):
        _create_analysis(db_session, upload, status="RUNNING")
        _create_analysis(db_session, upload, status="COMPLETED")
        db_session.commit()

        result = query_service.list_upload_analyses(db_session, user.id, upload.id)

        assert len(result.items) == 2

    def test_pagination(self, db_session: Session, user: User, upload: Upload):
        for i in range(4):
            _create_analysis(db_session, upload)
        db_session.commit()

        result = query_service.list_upload_analyses(db_session, user.id, upload.id, page=2, size=3)

        assert len(result.items) == 1
        assert result.total == 4
        assert result.page == 2

    def test_upload_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException) as exc:
            query_service.list_upload_analyses(db_session, user.id, 9999)
        assert "Upload" in str(exc.value.detail["message"])

    def test_upload_not_owned(self, db_session: Session, other_user: User, upload: Upload):
        with pytest.raises(NotFoundException):
            query_service.list_upload_analyses(db_session, other_user.id, upload.id)


# ─── Ownership validation ────────────────────────────────────────────


class TestOwnershipValidation:
    def test_all_endpoints_reject_unowned_analysis(self, db_session: Session, other_user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        for handler in [
            lambda: query_service.get_analysis_summary(db_session, other_user.id, analysis.id),
            lambda: query_service.get_analysis_files(db_session, other_user.id, analysis.id),
            lambda: query_service.get_analysis_technologies(db_session, other_user.id, analysis.id),
            lambda: query_service.get_analysis_dependencies(db_session, other_user.id, analysis.id),
            lambda: query_service.get_analysis_metrics(db_session, other_user.id, analysis.id),
            lambda: query_service.get_analysis_warnings(db_session, other_user.id, analysis.id),
        ]:
            with pytest.raises(NotFoundException, match="Analysis"):
                handler()

    def test_all_endpoints_reject_nonexistent_analysis(self, db_session: Session, user: User):
        for handler in [
            lambda: query_service.get_analysis_summary(db_session, user.id, 9999),
            lambda: query_service.get_analysis_files(db_session, user.id, 9999),
            lambda: query_service.get_analysis_technologies(db_session, user.id, 9999),
            lambda: query_service.get_analysis_dependencies(db_session, user.id, 9999),
            lambda: query_service.get_analysis_metrics(db_session, user.id, 9999),
            lambda: query_service.get_analysis_warnings(db_session, user.id, 9999),
        ]:
            with pytest.raises(NotFoundException, match="Analysis"):
                handler()


# ─── DTO mapping ─────────────────────────────────────────────────────


class TestDTOMapping:
    def test_summary_response_from_orm(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload, completed_at=datetime.datetime(2026, 7, 26, 12, 0, 0))
        db_session.commit()

        result = query_service.get_analysis_summary(db_session, user.id, analysis.id)

        assert result.analysis_id == analysis.id
        assert isinstance(result.created_at, datetime.datetime)

    def test_technology_response_dto_not_orm(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id)
        db_session.commit()

        result = query_service.get_analysis_technologies(db_session, user.id, analysis.id)

        t = result[0]
        assert hasattr(t, "name")
        assert not hasattr(t, "technology_id")

    def test_dependency_response_source_files_is_list(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, source_files=json.dumps(["a.txt", "b.txt"]))
        db_session.commit()

        result = query_service.get_analysis_dependencies(db_session, user.id, analysis.id)

        assert isinstance(result.items[0].source_files, list)


# ─── Deterministic ordering ──────────────────────────────────────────


class TestDeterministicOrdering:
    def test_files_sorted_by_relative_path_default(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        for name in ["b.py", "a.py", "c.py"]:
            _add_file(db_session, analysis.id, relative_path=name, file_name=name)
        db_session.commit()

        r1 = query_service.get_analysis_files(db_session, user.id, analysis.id)
        r2 = query_service.get_analysis_files(db_session, user.id, analysis.id)

        assert [f.relative_path for f in r1.items] == [f.relative_path for f in r2.items]

    def test_technologies_deterministic(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id, name="Zoo")
        _add_technology(db_session, analysis.id, name="Alpha")
        db_session.commit()

        r1 = query_service.get_analysis_technologies(db_session, user.id, analysis.id)
        r2 = query_service.get_analysis_technologies(db_session, user.id, analysis.id)

        assert [t.name for t in r1] == [t.name for t in r2]


# ─── No writes ────────────────────────────────────────────────────────


class TestNoWrites:
    def test_query_service_never_commits(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        query_service.get_analysis_summary(db_session, user.id, analysis.id)
        query_service.get_analysis_files(db_session, user.id, analysis.id)
        query_service.get_analysis_technologies(db_session, user.id, analysis.id)
        query_service.get_analysis_dependencies(db_session, user.id, analysis.id)
        query_service.get_analysis_metrics(db_session, user.id, analysis.id)
        query_service.get_analysis_warnings(db_session, user.id, analysis.id)

        assert True

    def test_repository_never_commits_on_read(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        file = _add_file(db_session, analysis.id, relative_path="temp.txt")
        db_session.commit()

        from app.modules.analysis import repository as repo

        repo.list_analysis_files_paginated(db_session, analysis.id)
        repo.list_dependencies_paginated(db_session, analysis.id)
        repo.list_warnings_paginated(db_session, analysis.id)
        repo.list_analysis_technologies_with_tech(db_session, analysis.id)
        repo.count_analysis_files(db_session, analysis.id)

        assert True


# ─── Empty analysis ──────────────────────────────────────────────────


class TestEmptyAnalysis:
    def test_all_endpoints_on_empty_analysis(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        summary = query_service.get_analysis_summary(db_session, user.id, analysis.id)
        assert summary.file_count == 0
        assert summary.dependency_count == 0
        assert summary.metric_count == 0
        assert summary.technology_count == 0
        assert summary.warning_count == 0

        files = query_service.get_analysis_files(db_session, user.id, analysis.id)
        assert len(files.items) == 0

        techs = query_service.get_analysis_technologies(db_session, user.id, analysis.id)
        assert techs == []

        deps = query_service.get_analysis_dependencies(db_session, user.id, analysis.id)
        assert len(deps.items) == 0

        metrics = query_service.get_analysis_metrics(db_session, user.id, analysis.id)
        assert metrics == []

        warnings = query_service.get_analysis_warnings(db_session, user.id, analysis.id)
        assert len(warnings.items) == 0

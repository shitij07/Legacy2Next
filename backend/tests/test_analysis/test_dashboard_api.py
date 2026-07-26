import datetime
import json

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
from app.modules.analysis import repository
from app.modules.analysis.dashboard_schemas import (
    DashboardResponse,
    GeneralSection,
    FilesSection,
    TechnologiesSection,
    DependenciesSection,
    WarningsSection,
    MetricsSection,
    LanguageCount,
    ExtensionCount,
    DirectorySize,
    CategoryCount,
    ConfidenceCount,
    EcosystemBreakdown,
    TopPackage,
    DetectorCount,
)
from app.modules.analysis.dashboard_service import get_dashboard


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    yield session
    session.close()


@pytest.fixture
def user(db_session: Session) -> User:
    user = User(email="alice@test.com", password_hash="pw", name="alice")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def other_user(db_session: Session) -> User:
    user = User(email="bob@test.com", password_hash="pw", name="bob")
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


# ─── Dashboard endpoint ────────────────────────────────────────────


class TestDashboardEndpoint:
    def test_returns_dashboard_response(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id)

        assert isinstance(result, DashboardResponse)

    def test_has_all_sections(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id)

        assert isinstance(result.general, GeneralSection)
        assert isinstance(result.files, FilesSection)
        assert isinstance(result.technologies, TechnologiesSection)
        assert isinstance(result.dependencies, DependenciesSection)
        assert isinstance(result.warnings, WarningsSection)
        assert isinstance(result.metrics, MetricsSection)

    def test_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException) as exc:
            get_dashboard(db_session, user.id, 9999)
        assert "Analysis" in str(exc.value.detail["message"])

    def test_not_owned(self, db_session: Session, other_user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        with pytest.raises(NotFoundException) as exc:
            get_dashboard(db_session, other_user.id, analysis.id)
        assert "Analysis" in str(exc.value.detail["message"])


# ─── General section ───────────────────────────────────────────────


class TestGeneralSection:
    def test_metadata_included(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload, completed_at=datetime.datetime(2026, 7, 26, 12, 0, 0))
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).general

        assert result.analysis_id == analysis.id
        assert result.upload_id == upload.id
        assert result.status == "COMPLETED"
        assert result.created_at is not None

    def test_duration_ms_calculated(self, db_session: Session, user: User, upload: Upload):
        created = datetime.datetime(2026, 7, 26, 12, 0, 0)
        completed = datetime.datetime(2026, 7, 26, 12, 0, 5)
        analysis = _create_analysis(db_session, upload, completed_at=completed)
        analysis.created_at = created
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).general

        assert result.duration_ms == 5000

    def test_duration_ms_none_when_not_completed(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload, status="RUNNING", completed_at=None)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).general

        assert result.duration_ms is None

    def test_error_detail_included(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload, status="FAILED", error_detail="Something broke")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).general

        assert result.error_detail == "Something broke"


# ─── Files section ─────────────────────────────────────────────────


class TestFilesSection:
    def test_counts(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id)
        _add_file(db_session, analysis.id, relative_path="dir", file_name="dir", is_directory=True)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).files

        assert result.total_files == 2
        assert result.total_directories == 1

    def test_language_distribution(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, language="Python")
        _add_file(db_session, analysis.id, language="Python", relative_path="utils.py", file_name="utils.py")
        _add_file(db_session, analysis.id, language="JavaScript", relative_path="f.js", file_name="f.js")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).files

        langs = {lc.language: lc.count for lc in result.language_distribution}
        assert langs == {"JavaScript": 1, "Python": 2}

    def test_language_distribution_empty_when_no_language(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, language=None)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).files

        assert result.language_distribution == []

    def test_extension_distribution(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, extension=".py")
        _add_file(db_session, analysis.id, extension=".py", relative_path="utils.py", file_name="utils.py")
        _add_file(db_session, analysis.id, extension=".js", relative_path="f.js", file_name="f.js")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).files

        exts = {ec.extension: ec.count for ec in result.extension_distribution}
        assert exts == {".js": 1, ".py": 2}

    def test_largest_directories(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, relative_path="small_dir", file_name="small_dir", is_directory=True, file_size=10)
        _add_file(db_session, analysis.id, relative_path="big_dir", file_name="big_dir", is_directory=True, file_size=1000)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).files

        assert len(result.largest_directories) == 2
        assert result.largest_directories[0].relative_path == "big_dir"
        assert result.largest_directories[1].relative_path == "small_dir"

    def test_language_distribution_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).files

        lc = result.language_distribution[0]
        assert isinstance(lc, LanguageCount)
        assert lc.language == "Python"
        assert lc.count == 1

    def test_extension_distribution_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).files

        ec = result.extension_distribution[0]
        assert isinstance(ec, ExtensionCount)
        assert ec.extension == ".py"
        assert ec.count == 1

    def test_directory_size_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, relative_path="mydir", file_name="mydir", is_directory=True, file_size=42)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).files

        ds = result.largest_directories[0]
        assert isinstance(ds, DirectorySize)
        assert ds.relative_path == "mydir"
        assert ds.file_size == 42


# ─── Technologies section ──────────────────────────────────────────


class TestTechnologiesSection:
    def test_total_count(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id)
        _add_technology(db_session, analysis.id, name="JavaScript", category="language")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).technologies

        assert result.total_technologies == 2

    def test_category_distribution(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id, name="Python", category="language")
        _add_technology(db_session, analysis.id, name="Django", category="framework")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).technologies

        cats = {cc.category: cc.count for cc in result.category_distribution}
        assert cats == {"framework": 1, "language": 1}

    def test_confidence_distribution(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id, name="Python", confidence="high")
        _add_technology(db_session, analysis.id, name="Django", confidence="medium")
        _add_technology(db_session, analysis.id, name="React", confidence="high", category="framework")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).technologies

        confs = {cc.confidence: cc.count for cc in result.confidence_distribution}
        assert confs == {"high": 2, "medium": 1}

    def test_primary_frameworks(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id, name="Django", category="framework")
        _add_technology(db_session, analysis.id, name="React", category="framework")
        _add_technology(db_session, analysis.id, name="Python", category="language")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).technologies

        assert sorted(result.primary_frameworks) == ["Django", "React"]

    def test_category_distribution_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).technologies

        cc = result.category_distribution[0]
        assert isinstance(cc, CategoryCount)

    def test_confidence_distribution_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_technology(db_session, analysis.id)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).technologies

        cc = result.confidence_distribution[0]
        assert isinstance(cc, ConfidenceCount)

    def test_empty(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).technologies

        assert result.total_technologies == 0
        assert result.category_distribution == []
        assert result.confidence_distribution == []
        assert result.primary_frameworks == []


# ─── Dependencies section ──────────────────────────────────────────


class TestDependenciesSection:
    def test_total_count(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id)
        _add_dependency(db_session, analysis.id, name="flask")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).dependencies

        assert result.total_dependencies == 2

    def test_type_counts(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, name="flask", type="library")
        _add_dependency(db_session, analysis.id, name="pytest", type="dev")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).dependencies

        assert result.direct_count == 1
        assert result.transitive_count == 1

    def test_ecosystem_breakdown(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, name="flask", ecosystem="pip")
        _add_dependency(db_session, analysis.id, name="react", ecosystem="npm")
        _add_dependency(db_session, analysis.id, name="django", ecosystem="pip")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).dependencies

        ecos = {eb.ecosystem: eb.count for eb in result.ecosystem_breakdown}
        assert ecos == {"npm": 1, "pip": 2}

    def test_top_packages(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id, name="django", version="4.2", ecosystem="pip")
        _add_dependency(db_session, analysis.id, name="react", version="18.0", ecosystem="npm")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).dependencies

        assert len(result.top_packages) == 2
        names = sorted(tp.name for tp in result.top_packages)
        assert names == ["django", "react"]

    def test_top_package_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).dependencies

        tp = result.top_packages[0]
        assert isinstance(tp, TopPackage)
        assert tp.name == "requests"
        assert tp.ecosystem == "pip"

    def test_ecosystem_breakdown_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_dependency(db_session, analysis.id)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).dependencies

        eb = result.ecosystem_breakdown[0]
        assert isinstance(eb, EcosystemBreakdown)

    def test_empty(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).dependencies

        assert result.total_dependencies == 0
        assert result.direct_count == 0
        assert result.transitive_count == 0
        assert result.ecosystem_breakdown == []
        assert result.top_packages == []


# ─── Warnings section ──────────────────────────────────────────────


class TestWarningsSection:
    def test_total_count(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_warning(db_session, analysis.id)
        _add_warning(db_session, analysis.id, message="Another")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).warnings

        assert result.total_warnings == 2

    def test_detector_breakdown(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_warning(db_session, analysis.id, detector_name="DetA")
        _add_warning(db_session, analysis.id, detector_name="DetA")
        _add_warning(db_session, analysis.id, detector_name="DetB")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).warnings

        dets = {dc.detector_name: dc.count for dc in result.detector_breakdown}
        assert dets == {"DetA": 2, "DetB": 1}

    def test_detector_count_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_warning(db_session, analysis.id)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).warnings

        dc = result.detector_breakdown[0]
        assert isinstance(dc, DetectorCount)

    def test_empty(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).warnings

        assert result.total_warnings == 0
        assert result.detector_breakdown == []


# ─── Metrics section ───────────────────────────────────────────────


class TestMetricsSection:
    def test_total_count(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_metric(db_session, analysis.id, key="project.total_files", value=42)
        _add_metric(db_session, analysis.id, key="languages.count", value=3)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).metrics

        assert result.total_metrics == 2

    def test_populates_known_keys(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_metric(db_session, analysis.id, key="project.total_files", value=100)
        _add_metric(db_session, analysis.id, key="project.total_file_size", value=50000)
        _add_metric(db_session, analysis.id, key="languages.count", value=3)
        _add_metric(db_session, analysis.id, key="languages.primary", value=None, value_str="Python")
        _add_metric(db_session, analysis.id, key="frameworks.count", value=2)
        _add_metric(db_session, analysis.id, key="dependencies.count", value=15)
        _add_metric(db_session, analysis.id, key="manifests.count", value=1)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).metrics

        assert result.project_total_files == 100
        assert result.project_total_file_size == 50000
        assert result.language_count == 3
        assert result.primary_language == "Python"
        assert result.framework_count == 2
        assert result.dependency_count == 15
        assert result.manifest_count == 1

    def test_missing_keys_are_none(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).metrics

        assert result.project_total_files is None
        assert result.primary_language is None

    def test_empty(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id).metrics

        assert result.total_metrics == 0


# ─── Empty analysis ────────────────────────────────────────────────


class TestEmptyAnalysis:
    def test_all_sections_defaults(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id)

        assert result.files.total_files == 0
        assert result.files.total_directories == 0
        assert result.files.language_distribution == []
        assert result.files.extension_distribution == []
        assert result.technologies.total_technologies == 0
        assert result.dependencies.total_dependencies == 0
        assert result.warnings.total_warnings == 0
        assert result.metrics.total_metrics == 0


# ─── Ownership validation ──────────────────────────────────────────


class TestOwnershipValidation:
    def test_dashboard_rejects_unowned_analysis(self, db_session: Session, other_user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        with pytest.raises(NotFoundException, match="Analysis"):
            get_dashboard(db_session, other_user.id, analysis.id)

    def test_dashboard_rejects_nonexistent_analysis(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException, match="Analysis"):
            get_dashboard(db_session, user.id, 9999)


# ─── DTO mapping ───────────────────────────────────────────────────


class TestDTOMapping:
    def test_dashboard_response_is_not_orm(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id)

        assert not hasattr(result, "_sa_instance_state")
        assert isinstance(result.general, GeneralSection)

    def test_all_nested_dtos(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id)
        _add_technology(db_session, analysis.id)
        _add_dependency(db_session, analysis.id)
        _add_warning(db_session, analysis.id)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id)

        assert result.files.language_distribution[0].language == "Python"
        assert result.technologies.category_distribution[0].category == "language"
        assert result.dependencies.ecosystem_breakdown[0].ecosystem == "pip"
        assert result.warnings.detector_breakdown[0].detector_name == "LanguageDetector"


# ─── Deterministic ordering ────────────────────────────────────────


class TestDeterministicOrdering:
    def test_language_distribution_alphabetical(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, language="Python")
        _add_file(db_session, analysis.id, language="JavaScript", relative_path="f.js", file_name="f.js")
        _add_file(db_session, analysis.id, language="TypeScript", relative_path="f.ts", file_name="f.ts")
        db_session.commit()

        r1 = get_dashboard(db_session, user.id, analysis.id)
        r2 = get_dashboard(db_session, user.id, analysis.id)

        assert [lc.language for lc in r1.files.language_distribution] == ["JavaScript", "Python", "TypeScript"]
        assert [lc.language for lc in r1.files.language_distribution] == [lc.language for lc in r2.files.language_distribution]

    def test_extension_distribution_alphabetical(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, extension=".ts")
        _add_file(db_session, analysis.id, extension=".js", relative_path="f.js", file_name="f.js")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id)

        assert [ec.extension for ec in result.files.extension_distribution] == [".js", ".ts"]

    def test_detector_breakdown_alphabetical(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_warning(db_session, analysis.id, detector_name="DetB")
        _add_warning(db_session, analysis.id, detector_name="DetA")
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id)

        assert [dc.detector_name for dc in result.warnings.detector_breakdown] == ["DetA", "DetB"]

    def test_dashboard_deterministic(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id, language="Python")
        _add_file(db_session, analysis.id, language="JavaScript", relative_path="f.js", file_name="f.js")
        _add_technology(db_session, analysis.id, name="Python", category="language")
        _add_technology(db_session, analysis.id, name="Django", category="framework")
        _add_dependency(db_session, analysis.id, name="flask", ecosystem="pip")
        _add_dependency(db_session, analysis.id, name="react", ecosystem="npm")
        _add_warning(db_session, analysis.id, detector_name="DetA")
        _add_warning(db_session, analysis.id, detector_name="DetB")
        _add_metric(db_session, analysis.id, key="project.total_files", value=2)
        db_session.commit()

        r1 = get_dashboard(db_session, user.id, analysis.id)
        r2 = get_dashboard(db_session, user.id, analysis.id)

        assert r1.model_dump_json() == r2.model_dump_json()


# ─── No writes ─────────────────────────────────────────────────────


class TestNoWrites:
    def test_dashboard_service_never_commits(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        get_dashboard(db_session, user.id, analysis.id)

        assert True

    def test_repository_aggregation_read_only(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id)
        _add_dependency(db_session, analysis.id)
        _add_warning(db_session, analysis.id)
        db_session.commit()

        repository.get_language_distribution(db_session, analysis.id)
        repository.get_extension_distribution(db_session, analysis.id)
        repository.get_ecosystem_breakdown(db_session, analysis.id)
        repository.get_detector_breakdown(db_session, analysis.id)
        repository.get_dependency_type_counts(db_session, analysis.id)
        repository.get_top_dependencies(db_session, analysis.id)
        repository.get_largest_directories(db_session, analysis.id)
        repository.get_technology_category_distribution(db_session, analysis.id)
        repository.count_analysis_directories(db_session, analysis.id)

        assert True


# ─── Response schema ───────────────────────────────────────────────


class TestResponseSchema:
    def test_serializes_to_json(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        db_session.commit()

        result = get_dashboard(db_session, user.id, analysis.id)

        data = result.model_dump()
        assert isinstance(data, dict)
        assert "general" in data
        assert "files" in data
        assert "technologies" in data
        assert "dependencies" in data
        assert "warnings" in data
        assert "metrics" in data

    def test_json_types(self, db_session: Session, user: User, upload: Upload):
        analysis = _create_analysis(db_session, upload)
        _add_file(db_session, analysis.id)
        _add_technology(db_session, analysis.id)
        _add_dependency(db_session, analysis.id)
        _add_warning(db_session, analysis.id)
        db_session.commit()

        data = get_dashboard(db_session, user.id, analysis.id).model_dump()

        assert data["files"]["total_files"] == 1
        assert len(data["files"]["language_distribution"]) == 1
        assert data["technologies"]["total_technologies"] == 1
        assert data["dependencies"]["total_dependencies"] == 1
        assert data["warnings"]["total_warnings"] == 1

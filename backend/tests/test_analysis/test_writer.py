import datetime
import json

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
from app.modules.analysis.types import (
    AnalysisResults,
    DetectedDependency,
    DetectedFile,
    DetectedMetric,
    DetectedTechnology,
    DetectorResult,
    DetectorWarning,
)
from app.modules.analysis.writer import AnalysisWriter, PersistenceResult


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    yield session
    session.close()


@pytest.fixture
def writer() -> AnalysisWriter:
    return AnalysisWriter()


@pytest.fixture
def analysis(db_session: Session) -> Analysis:
    user = User(email="test@example.com", password_hash="abc", name="testuser")
    db_session.add(user)
    db_session.flush()
    project = Project(user_id=user.id, name="test-project")
    db_session.add(project)
    db_session.flush()
    upload = Upload(
        project_id=project.id,
        original_name="test.zip",
        stored_name="abc123",
        file_path="/tmp/uploads",
        file_size=100,
        mime_type="application/zip",
        extension=".zip",
        sha256_hash="abc",
    )
    db_session.add(upload)
    db_session.flush()
    analysis = Analysis(upload_id=upload.id, status="PENDING")
    db_session.add(analysis)
    db_session.flush()
    db_session.commit()
    return analysis


def _make_results(
    files: list[DetectedFile] | None = None,
    technologies: list[DetectedTechnology] | None = None,
    dependencies: list[DetectedDependency] | None = None,
    metrics: list[DetectedMetric] | None = None,
    warnings: list[DetectorWarning] | None = None,
    errors: list[str] | None = None,
) -> AnalysisResults:
    results: list[DetectorResult] = []
    if files or technologies or dependencies or metrics or warnings or errors:
        results.append(DetectorResult(
            detector_name="TestDetector",
            files=tuple(files or []),
            technologies=tuple(technologies or []),
            dependencies=tuple(dependencies or []),
            metrics=tuple(metrics or []),
            warnings=tuple(warnings or []),
            error=errors[0] if errors else None,
        ))
    if errors and len(errors) > 1:
        for err in errors[1:]:
            results.append(DetectorResult(
                detector_name="OtherDetector",
                error=err,
            ))
    return AnalysisResults(results=results, start_time=0.0, end_time=1.0)


# ─── Successful persistence ─────────────────────────────────────────


class TestSuccessfulPersistence:
    def test_files_persisted(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        files = [
            DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=100, language="Python"),
            DetectedFile(relative_path="utils.py", file_name="utils.py", extension=".py", file_size=200, language="Python"),
        ]
        results = _make_results(files=files)
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.file_count == 2
        persisted = db_session.query(AnalysisFile).filter(AnalysisFile.analysis_id == analysis.id).all()
        assert len(persisted) == 2
        paths = sorted(f.relative_path for f in persisted)
        assert paths == ["main.py", "utils.py"]

    def test_technologies_persisted(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        techs = [
            DetectedTechnology(name="Python", category="language", evidence="5 files (100%)"),
            DetectedTechnology(name="Django", category="framework", evidence="requirements.txt"),
        ]
        results = _make_results(technologies=techs)
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.technology_count == 2
        persisted = db_session.query(AnalysisTechnology).filter(AnalysisTechnology.analysis_id == analysis.id).all()
        assert len(persisted) == 2

    def test_technologies_normalized(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        techs = [
            DetectedTechnology(name="Python", category="language"),
            DetectedTechnology(name="Python", category="language"),
        ]
        results = _make_results(technologies=techs)
        writer.write(db_session, analysis.id, results)
        db_session.commit()

        tech_rows = db_session.query(Technology).filter(Technology.name == "Python").all()
        assert len(tech_rows) == 1

    def test_dependencies_persisted(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        deps = [
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip", source_files=("requirements.txt",)),
            DetectedDependency(name="django", version="5.0.0", ecosystem="pip", source_files=("requirements.txt",)),
        ]
        results = _make_results(dependencies=deps)
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.dependency_count == 2
        persisted = db_session.query(Dependency).filter(Dependency.analysis_id == analysis.id).all()
        assert len(persisted) == 2

    def test_metrics_int_persisted(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results(metrics=[
            DetectedMetric(key="total_files", value=42),
        ])
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.metric_count == 1
        metric = db_session.query(Metric).filter(Metric.analysis_id == analysis.id).first()
        assert metric is not None
        assert metric.key == "total_files"
        assert metric.value == 42
        assert metric.value_str is None

    def test_metrics_string_persisted(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results(metrics=[
            DetectedMetric(key="primary_language", value="Python"),
        ])
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.metric_count == 1
        metric = db_session.query(Metric).filter(Metric.analysis_id == analysis.id).first()
        assert metric is not None
        assert metric.key == "primary_language"
        assert metric.value is None
        assert metric.value_str == "Python"

    def test_metric_invariant_enforced(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results(metrics=[
            DetectedMetric(key="files", value=10),
            DetectedMetric(key="primary_lang", value="Python"),
        ])
        writer.write(db_session, analysis.id, results)
        db_session.commit()

        metrics = db_session.query(Metric).filter(Metric.analysis_id == analysis.id).order_by(Metric.key).all()
        int_metric = next(m for m in metrics if m.key == "files")
        str_metric = next(m for m in metrics if m.key == "primary_lang")
        assert int_metric.value == 10
        assert int_metric.value_str is None
        assert str_metric.value is None
        assert str_metric.value_str == "Python"

    def test_warnings_persisted(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        warnings = [
            DetectorWarning(detector_name="DepDetector", message="Version conflict for requests"),
            DetectorWarning(detector_name="DepDetector", message="Partial parse"),
        ]
        results = _make_results(warnings=warnings)
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.warning_count == 2
        persisted = db_session.query(AnalysisWarning).filter(AnalysisWarning.analysis_id == analysis.id).all()
        assert len(persisted) == 2
        messages = sorted(w.message for w in persisted)
        assert messages == ["Partial parse", "Version conflict for requests"]

    def test_empty_results(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results()
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.file_count == 0
        assert result.technology_count == 0
        assert result.dependency_count == 0
        assert result.metric_count == 0
        assert result.warning_count == 0


# ─── Source files ──────────────────────────────────────────────────


class TestSourceFiles:
    def test_single_source_file(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        deps = [
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip", source_files=("requirements.txt",)),
        ]
        results = _make_results(dependencies=deps)
        writer.write(db_session, analysis.id, results)
        db_session.commit()

        dep = db_session.query(Dependency).filter(Dependency.analysis_id == analysis.id).first()
        assert dep is not None
        assert dep.source_file == "requirements.txt"
        assert json.loads(dep.source_files) == ["requirements.txt"]

    def test_multiple_source_files(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        deps = [
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip", source_files=("requirements.txt", "setup.py")),
        ]
        results = _make_results(dependencies=deps)
        writer.write(db_session, analysis.id, results)
        db_session.commit()

        dep = db_session.query(Dependency).filter(Dependency.analysis_id == analysis.id).first()
        assert dep is not None
        assert json.loads(dep.source_files) == ["requirements.txt", "setup.py"]

    def test_no_source_files(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        deps = [
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip", source_files=()),
        ]
        results = _make_results(dependencies=deps)
        writer.write(db_session, analysis.id, results)
        db_session.commit()

        dep = db_session.query(Dependency).filter(Dependency.analysis_id == analysis.id).first()
        assert dep is not None
        assert dep.source_file is None
        assert dep.source_files is None


# ─── Error aggregation ─────────────────────────────────────────────


class TestErrorAggregation:
    def test_no_errors(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results()
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.error_detail is None
        updated = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
        assert updated.error_detail is None
        assert updated.status == "COMPLETED"

    def test_single_error(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results(errors=["Detector crashed"])
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.error_detail is not None
        assert "TestDetector: Detector crashed" in result.error_detail

    def test_multiple_errors_sorted(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results(errors=["Error B", "Error A"])
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.error_detail is not None
        assert result.error_detail == "OtherDetector: Error A; TestDetector: Error B"

    def test_error_detail_on_analysis(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results(errors=["Something failed"])
        writer.write(db_session, analysis.id, results)
        db_session.commit()

        updated = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
        assert updated.error_detail is not None
        assert "Something failed" in updated.error_detail
        assert updated.status == "COMPLETED_WITH_ERRORS"


# ─── Status ─────────────────────────────────────────────────────────


class TestStatus:
    def test_status_completed(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results()
        writer.write(db_session, analysis.id, results)
        db_session.commit()

        updated = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
        assert updated.status == "COMPLETED"
        assert updated.completed_at is not None

    def test_status_with_errors(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results(errors=["Failed"])
        writer.write(db_session, analysis.id, results)
        db_session.commit()

        updated = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
        assert updated.status == "COMPLETED_WITH_ERRORS"
        assert updated.completed_at is not None

    def test_status_pending_before_write(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        assert analysis.status == "PENDING"


# ─── Determinism ────────────────────────────────────────────────────


class TestDeterminism:
    def test_deterministic_persistence(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        files = [
            DetectedFile(relative_path="b.py", file_name="b.py", extension=".py", file_size=200, language="Python"),
            DetectedFile(relative_path="a.py", file_name="a.py", extension=".py", file_size=100, language="Python"),
        ]
        results = _make_results(files=files)
        writer.write(db_session, analysis.id, results)
        db_session.commit()

        persisted = db_session.query(AnalysisFile).filter(AnalysisFile.analysis_id == analysis.id).order_by(AnalysisFile.relative_path).all()
        assert persisted[0].relative_path == "a.py"
        assert persisted[1].relative_path == "b.py"


# ─── Writer boundary ────────────────────────────────────────────────


class TestWriterBoundary:
    def test_writer_never_commits(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results(files=[
            DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=100, language="Python"),
        ])
        writer.write(db_session, analysis.id, results)
        persisted = db_session.query(AnalysisFile).filter(AnalysisFile.analysis_id == analysis.id).all()
        assert len(persisted) == 0

    def test_writer_returns_persistence_result(self, writer: AnalysisWriter):
        result = PersistenceResult(
            analysis_id=1,
            file_count=0,
            technology_count=0,
            dependency_count=0,
            metric_count=0,
            warning_count=0,
            error_detail=None,
        )
        assert isinstance(result, PersistenceResult)
        assert result.file_count == 0

    def test_dependency_dedup(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        deps = [
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip"),
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip"),
        ]
        results = _make_results(dependencies=deps)
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.dependency_count == 1
        persisted = db_session.query(Dependency).filter(Dependency.analysis_id == analysis.id).all()
        assert len(persisted) == 1

    def test_metric_dedup(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = _make_results(metrics=[
            DetectedMetric(key="total_files", value=42),
            DetectedMetric(key="total_files", value=43),
        ])
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.metric_count == 1
        persisted = db_session.query(Metric).filter(Metric.analysis_id == analysis.id).all()
        assert len(persisted) == 1
        assert persisted[0].value == 42  # first occurrence wins


# ─── Partial detector failures ──────────────────────────────────────


class TestPartialFailures:
    def test_some_detectors_failed(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        results = AnalysisResults(
            results=[
                DetectorResult(
                    detector_name="GoodDetector",
                    technologies=(DetectedTechnology(name="React", category="framework"),),
                    error=None,
                ),
                DetectorResult(
                    detector_name="BadDetector",
                    error="Crashed",
                ),
            ],
            start_time=0.0,
            end_time=1.0,
        )
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.technology_count == 1
        assert result.error_detail is not None
        assert "BadDetector: Crashed" in result.error_detail
        updated = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
        assert updated.status == "COMPLETED_WITH_ERRORS"


# ─── Full integration ───────────────────────────────────────────────


class TestIntegration:
    def test_full_write(self, db_session: Session, analysis: Analysis, writer: AnalysisWriter):
        files = [
            DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=100, language="Python"),
        ]
        techs = [
            DetectedTechnology(name="Python", category="language"),
            DetectedTechnology(name="Django", category="framework"),
        ]
        deps = [
            DetectedDependency(name="django", version="5.0.0", ecosystem="pip", source_files=("requirements.txt",)),
        ]
        metrics = [
            DetectedMetric(key="total_files", value=1),
            DetectedMetric(key="primary_language", value="Python"),
        ]
        warnings = [
            DetectorWarning(detector_name="DepDetector", message="Version conflict"),
        ]
        results = _make_results(files=files, technologies=techs, dependencies=deps, metrics=metrics, warnings=warnings)
        result = writer.write(db_session, analysis.id, results)
        db_session.commit()

        assert result.file_count == 1
        assert result.technology_count == 2
        assert result.dependency_count == 1
        assert result.metric_count == 2
        assert result.warning_count == 1
        assert result.error_detail is None

        updated = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
        assert updated.status == "COMPLETED"
        assert updated.completed_at is not None

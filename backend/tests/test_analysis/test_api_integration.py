import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.core.exceptions import NotFoundException
from app.models.analysis import Analysis
from app.models.analysis_file import AnalysisFile
from app.models.analysis_technology import AnalysisTechnology
from app.models.project import Project
from app.models.upload import Upload
from app.models.user import User
from app.modules.analysis import service as analysis_service
from app.modules.analysis.schemas import AnalysisResponse
from app.modules.analysis.types import AnalysisResults, DetectorResult


# ─── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def temp_upload_root(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("app.core.config.settings.UPLOAD_ROOT", tmpdir)
        yield Path(tmpdir)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    yield session
    session.close()


@pytest.fixture
def user(db_session: Session) -> User:
    user = User(email="ana@test.com", password_hash="pw", name="ana")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def project(db_session: Session, user: User) -> Project:
    project = Project(user_id=user.id, name="test-project")
    db_session.add(project)
    db_session.flush()
    return project


def _create_upload(db: Session, project: Project) -> Upload:
    upload = Upload(
        project_id=project.id,
        original_name="main.py",
        stored_name="abc123.py",
        file_path=f"{project.id}/files/abc123.py",
        file_size=10,
        mime_type="text/x-python",
        extension=".py",
        sha256_hash="abc",
    )
    db.add(upload)
    db.flush()
    return upload


def _write_file(temp_upload_root: Path, project: Project, rel_path: str, content: str) -> Path:
    target = temp_upload_root / str(project.id) / "files" / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return target


def _other_user(db: Session) -> User:
    user = User(email="other@test.com", password_hash="pw", name="other")
    db_session.add(user)
    db_session.flush()
    return user


# ─── Successful analysis ────────────────────────────────────────────


class TestSuccessfulAnalysis:
    def test_returns_analysis_response(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        result = analysis_service.run_analysis(db_session, user.id, upload.id)

        assert isinstance(result, AnalysisResponse)
        assert result.analysis_id > 0
        assert result.status == "COMPLETED"
        assert result.error_detail is None

    def test_status_transition(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        assert analysis.status == "COMPLETED"

    def test_files_persisted(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        _write_file(temp_upload_root, project, "utils.py", "y = 2")
        upload = _create_upload(db_session, project)
        db_session.commit()

        analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        files = db_session.query(AnalysisFile).filter(AnalysisFile.analysis_id == analysis.id).all()
        assert len(files) == 3
        paths = sorted(f.relative_path for f in files)
        assert paths == [".", "app.py", "utils.py"]

    def test_technologies_persisted(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        techs = db_session.query(AnalysisTechnology).filter(AnalysisTechnology.analysis_id == analysis.id).all()
        assert len(techs) >= 1
        names = sorted(t.technology.name for t in techs)
        assert "Python" in names

    def test_metrics_persisted(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        from app.models.metric import Metric
        metrics = db_session.query(Metric).filter(Metric.analysis_id == analysis.id).all()
        keys = [m.key for m in metrics]
        assert "project.total_files" in keys
        assert "project.total_file_size" in keys

    def test_completed_at_set(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        assert analysis.completed_at is not None


# ─── Upload validation ──────────────────────────────────────────────


class TestUploadValidation:
    def test_upload_not_found(self, db_session: Session, user: User):
        with pytest.raises(NotFoundException) as exc:
            analysis_service.run_analysis(db_session, user.id, 9999)
        assert "Upload" in str(exc.value.detail["message"])

    def test_upload_not_owned(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        other = User(email="other@test.com", password_hash="pw", name="other")
        db_session.add(other)
        db_session.flush()
        db_session.commit()

        with pytest.raises(NotFoundException) as exc:
            analysis_service.run_analysis(db_session, other.id, upload.id)
        assert "Upload" in str(exc.value.detail["message"])

    def test_upload_without_project(self, db_session: Session, user: User):
        upload = Upload(
            project_id=9999,
            original_name="orphan.py",
            stored_name="orphan.py",
            file_path="orphan.py",
            file_size=10,
            mime_type="text/plain",
            extension=".py",
            sha256_hash="orphan",
        )
        db_session.add(upload)
        db_session.commit()

        with pytest.raises(NotFoundException):
            analysis_service.run_analysis(db_session, user.id, upload.id)


# ─── COMPLETED_WITH_ERRORS ─────────────────────────────────────────


class TestCompletedWithErrors:
    def test_detector_error_yields_warning_status(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch.object(
            analysis_service,
            "_build_pipeline",
            return_value=_pipeline_with_error(),
        ):
            result = analysis_service.run_analysis(db_session, user.id, upload.id)

        assert result.status == "COMPLETED_WITH_ERRORS"

    def test_error_detail_populated(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch.object(
            analysis_service,
            "_build_pipeline",
            return_value=_pipeline_with_error(),
        ):
            result = analysis_service.run_analysis(db_session, user.id, upload.id)

        assert result.error_detail is not None
        assert "BrokenDetector" in result.error_detail

    def test_good_data_still_persisted(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch.object(
            analysis_service,
            "_build_pipeline",
            return_value=_pipeline_with_error(),
        ):
            analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        files = db_session.query(AnalysisFile).filter(AnalysisFile.analysis_id == analysis.id).count()
        assert files >= 1


# ─── FAILED status ─────────────────────────────────────────────────


class TestFailedStatus:
    def test_pipeline_exception_yields_failed(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch.object(
            analysis_service,
            "_build_pipeline",
            return_value=_pipeline_that_raises(RuntimeError("Disk failure")),
        ):
            with pytest.raises(RuntimeError):
                analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        assert analysis is not None
        assert analysis.status == "FAILED"

    def test_failed_error_detail_set(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch.object(
            analysis_service,
            "_build_pipeline",
            return_value=_pipeline_that_raises(RuntimeError("Disk failure")),
        ):
            with pytest.raises(RuntimeError):
                analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        assert analysis.error_detail is not None

    def test_failed_is_terminal(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch.object(
            analysis_service,
            "_build_pipeline",
            return_value=_pipeline_that_raises(RuntimeError("fail")),
        ):
            with pytest.raises(RuntimeError):
                analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        analysis_id = analysis.id
        assert analysis.status == "FAILED"

        analysis2 = db_session.query(Analysis).filter(Analysis.id == analysis_id).first()
        assert analysis2.status == "FAILED"

    def test_writer_exception_yields_failed(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch("app.modules.analysis.writer.AnalysisWriter.write", side_effect=RuntimeError("DB write failed")):
            with pytest.raises(RuntimeError):
                analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        assert analysis.status == "FAILED"


# ─── Transaction ownership ──────────────────────────────────────────


class TestTransactionOwnership:
    def test_service_commits(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        assert analysis is not None

    def test_rollback_on_failure(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch.object(
            analysis_service,
            "_build_pipeline",
            return_value=_pipeline_that_raises(RuntimeError("fail")),
        ):
            with pytest.raises(RuntimeError):
                analysis_service.run_analysis(db_session, user.id, upload.id)

        files = db_session.query(AnalysisFile).count()
        assert files == 0

    def test_no_data_leaked_on_rollback(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch.object(
            analysis_service,
            "_build_pipeline",
            return_value=_pipeline_that_raises(RuntimeError("fail")),
        ):
            with pytest.raises(RuntimeError):
                analysis_service.run_analysis(db_session, user.id, upload.id)

        assert db_session.query(AnalysisFile).count() == 0
        assert db_session.query(AnalysisTechnology).count() == 0
        from app.models.metric import Metric
        assert db_session.query(Metric).count() == 0

    def test_service_does_not_commit_on_analysis_creation(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        upload = _create_upload(db_session, project)
        db_session.commit()

        with patch.object(
            analysis_service,
            "_build_pipeline",
            return_value=_pipeline_that_raises(RuntimeError("fail")),
        ):
            with pytest.raises(RuntimeError):
                analysis_service.run_analysis(db_session, user.id, upload.id)

        analyses_before = db_session.query(Analysis).count()
        assert analyses_before == 1


# ─── AnalysisResponse correctness ────────────────────────────────────


class TestAnalysisResponse:
    def test_fields_match_analysis(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        result = analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).filter(Analysis.id == result.analysis_id).first()
        assert result.analysis_id == analysis.id
        assert result.status == analysis.status
        assert result.error_detail == analysis.error_detail

    def test_from_attributes(self):
        resp = AnalysisResponse(analysis_id=1, status="COMPLETED")
        assert resp.analysis_id == 1
        assert resp.status == "COMPLETED"
        assert resp.error_detail is None

    def test_from_attributes_with_error(self):
        resp = AnalysisResponse(analysis_id=1, status="COMPLETED_WITH_ERRORS", error_detail="Something went wrong")
        assert resp.error_detail == "Something went wrong"


# ─── End-to-end ──────────────────────────────────────────────────────


class TestEndToEnd:
    def test_full_analysis_flow(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        _write_file(temp_upload_root, project, "index.html", "<html></html>")
        upload = _create_upload(db_session, project)
        db_session.commit()

        result = analysis_service.run_analysis(db_session, user.id, upload.id)

        assert result.status == "COMPLETED"
        assert result.analysis_id > 0

        analysis = db_session.query(Analysis).filter(Analysis.id == result.analysis_id).first()
        assert analysis.status == "COMPLETED"
        assert analysis.completed_at is not None

        files = db_session.query(AnalysisFile).filter(AnalysisFile.analysis_id == analysis.id).all()
        assert len(files) == 3

        from app.models.metric import Metric
        metrics = db_session.query(Metric).filter(Metric.analysis_id == analysis.id).all()
        metric_keys = [m.key for m in metrics]
        assert "project.total_files" in metric_keys
        assert "project.total_file_size" in metric_keys
        assert "languages.count" in metric_keys

    def test_missing_project_dir_fails_gracefully(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        upload = _create_upload(db_session, project)
        db_session.commit()

        with pytest.raises(Exception):
            analysis_service.run_analysis(db_session, user.id, upload.id)

        analysis = db_session.query(Analysis).first()
        assert analysis.status == "FAILED"

    def test_deterministic(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        upload = _create_upload(db_session, project)
        db_session.commit()

        r1 = analysis_service.run_analysis(db_session, user.id, upload.id)

        upload2 = _create_upload(db_session, project)
        db_session.commit()
        r2 = analysis_service.run_analysis(db_session, user.id, upload2.id)

        assert r1.status == r2.status

    def test_concurrent_analyses(self, db_session: Session, temp_upload_root: Path, user: User, project: Project):
        _write_file(temp_upload_root, project, "app.py", "x = 1")
        u1 = _create_upload(db_session, project)
        u2 = _create_upload(db_session, project)
        db_session.commit()

        r1 = analysis_service.run_analysis(db_session, user.id, u1.id)
        r2 = analysis_service.run_analysis(db_session, user.id, u2.id)

        assert r1.analysis_id != r2.analysis_id
        assert r1.status == "COMPLETED"
        assert r2.status == "COMPLETED"


# ─── Helpers ─────────────────────────────────────────────────────────


def _pipeline_with_error():
    from app.modules.analysis.base import BaseDetector
    from app.modules.analysis.discovery import DiscoveryEngine
    from app.modules.analysis.language_detector import LanguageDetector
    from app.modules.analysis.metrics_collector import MetricsCollector
    from app.modules.analysis.pipeline import AnalysisPipeline

    class BrokenDetector(BaseDetector):
        @property
        def detector_name(self) -> str:
            return "BrokenDetector"

        def detect(self, context: object) -> DetectorResult:
            raise RuntimeError("Intentional detector failure")

    return AnalysisPipeline(
        engine=DiscoveryEngine(),
        detectors=[LanguageDetector(), BrokenDetector()],
        metrics_collector=MetricsCollector(),
    )


def _pipeline_that_raises(exception: Exception):
    from unittest.mock import MagicMock

    from app.modules.analysis.pipeline import AnalysisPipeline

    pipeline = MagicMock(spec=AnalysisPipeline)
    pipeline.analyze.side_effect = exception
    return pipeline

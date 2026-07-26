import logging
import time
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.models.analysis import Analysis
from app.modules.analysis import repository as analysis_repository
from app.modules.analysis.dependency_detector import DependencyDetector
from app.modules.analysis.discovery import DiscoveryEngine
from app.modules.analysis.framework_detector import FrameworkDetector
from app.modules.analysis.language_detector import LanguageDetector
from app.modules.analysis.metrics_collector import MetricsCollector
from app.modules.analysis.pipeline import AnalysisPipeline
from app.modules.analysis.schemas import AnalysisResponse
from app.modules.analysis.writer import AnalysisWriter
from app.modules.projects import repository as projects_repository
from app.modules.uploads import repository as uploads_repository

logger = logging.getLogger(__name__)


def _get_owned_upload(db: Session, user_id: int, upload_id: int):
    upload = uploads_repository.get_upload_by_id(db, upload_id)
    if upload is None:
        raise NotFoundException("Upload")
    project = projects_repository.get_project_by_id(db, upload.project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Upload")
    return upload


def _build_pipeline() -> AnalysisPipeline:
    engine = DiscoveryEngine()
    detectors = [
        LanguageDetector(),
        FrameworkDetector(),
        DependencyDetector(),
    ]
    metrics_collector = MetricsCollector()
    return AnalysisPipeline(
        engine=engine,
        detectors=detectors,
        metrics_collector=metrics_collector,
    )


def run_analysis(
    db: Session,
    user_id: int,
    upload_id: int,
) -> AnalysisResponse:
    upload = _get_owned_upload(db, user_id, upload_id)
    root_path = Path(settings.UPLOAD_ROOT) / str(upload.project_id) / "files"

    analysis = Analysis(upload_id=upload.id, status="RUNNING")
    db.add(analysis)
    db.flush()

    start = time.time()
    logger.info("Analysis %d started for upload %d", analysis.id, upload_id)

    try:
        pipeline = _build_pipeline()
        results = pipeline.analyze(
            root_path=root_path,
            upload_id=upload.id,
            project_id=upload.project_id,
        )

        writer = AnalysisWriter()
        writer.write(db, analysis.id, results)

        db.commit()
        db.refresh(analysis)

        duration = time.time() - start
        if analysis.status == "COMPLETED_WITH_ERRORS":
            logger.warning(
                "Analysis %d completed with errors in %.2fs",
                analysis.id, duration,
            )
        else:
            logger.info(
                "Analysis %d completed in %.2fs",
                analysis.id, duration,
            )

    except Exception:
        db.rollback()
        duration = time.time() - start
        logger.error(
            "Analysis %d failed after %.2fs",
            analysis.id, duration,
        )
        _try_set_failed(db, analysis)
        raise

    return AnalysisResponse(
        analysis_id=analysis.id,
        status=analysis.status,
        error_detail=analysis.error_detail,
    )


def _try_set_failed(db: Session, analysis: Analysis) -> None:
    try:
        analysis.status = "FAILED"
        analysis.error_detail = "Analysis failed before completion"
        db.add(analysis)
        db.commit()
    except Exception as e:
        logger.error(
            "Failed to persist FAILED status for analysis %d: %s",
            analysis.id, e,
        )
        db.rollback()

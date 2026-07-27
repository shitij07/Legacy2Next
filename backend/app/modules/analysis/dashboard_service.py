import logging
import time

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundException

from app.modules.analysis import repository

from app.modules.analysis.dashboard_schemas import (
    CategoryCount,
    ConfidenceCount,
    DashboardResponse,
    DependenciesSection,
    DetectorCount,
    DirectorySize,
    EcosystemBreakdown,
    ExtensionCount,
    FilesSection,
    GeneralSection,
    LanguageCount,
    MetricsSection,
    TechnologiesSection,
    TopPackage,
    WarningsSection,
)

logger = logging.getLogger(__name__)


def _get_owned_analysis(db: Session, user_id: int, analysis_id: int):
    analysis = repository.get_analysis_by_id(db, analysis_id)
    if analysis is None:
        raise NotFoundException("Analysis")
    upload = analysis.upload
    if upload is None:
        raise NotFoundException("Analysis")
    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, upload.project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Analysis")
    return analysis


def _duration_ms(analysis) -> int | None:
    if analysis.created_at and analysis.completed_at:
        delta = analysis.completed_at - analysis.created_at
        return int(delta.total_seconds() * 1000)
    return None


def get_dashboard(db: Session, user_id: int, analysis_id: int) -> DashboardResponse:
    _start = time.perf_counter()
    analysis = _get_owned_analysis(db, user_id, analysis_id)

    result = DashboardResponse(
        general=_build_general_section(analysis),
        files=_build_files_section(db, analysis.id),
        technologies=_build_technologies_section(db, analysis.id),
        dependencies=_build_dependencies_section(db, analysis.id),
        warnings=_build_warnings_section(db, analysis.id),
        metrics=_build_metrics_section(db, analysis.id),
    )

    _elapsed_ms = (time.perf_counter() - _start) * 1000
    if _elapsed_ms >= settings.SLOW_SERVICE_THRESHOLD_MS:
        logger.warning("get_dashboard(%d) took %.0fms", analysis_id, _elapsed_ms)
    else:
        logger.info("get_dashboard(%d) took %.0fms", analysis_id, _elapsed_ms)
    return result


def _build_general_section(analysis) -> GeneralSection:
    return GeneralSection(
        analysis_id=analysis.id,
        upload_id=analysis.upload_id,
        status=analysis.status,
        error_detail=analysis.error_detail,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        duration_ms=_duration_ms(analysis),
    )


def _build_files_section(db: Session, analysis_id: int) -> FilesSection:
    total_files = repository.count_analysis_files(db, analysis_id)
    total_directories = repository.count_analysis_directories(db, analysis_id)

    lang_rows = repository.get_language_distribution(db, analysis_id)
    language_distribution = [LanguageCount(language=lang, count=cnt) for lang, cnt in lang_rows]

    ext_rows = repository.get_extension_distribution(db, analysis_id)
    extension_distribution = [ExtensionCount(extension=ext, count=cnt) for ext, cnt in ext_rows]

    dir_rows = repository.get_largest_directories(db, analysis_id)
    largest_directories = [DirectorySize(relative_path=d.relative_path, file_size=d.file_size) for d in dir_rows]

    return FilesSection(
        total_files=total_files,
        total_directories=total_directories,
        language_distribution=language_distribution,
        extension_distribution=extension_distribution,
        largest_directories=largest_directories,
    )


def _build_technologies_section(db: Session, analysis_id: int) -> TechnologiesSection:
    rows = repository.list_analysis_technologies_with_tech(db, analysis_id)
    total = len(rows)

    category_map: dict[str, int] = {}
    confidence_map: dict[str, int] = {}
    frameworks: list[str] = []
    for row in rows:
        cat = row.technology.category
        category_map[cat] = category_map.get(cat, 0) + 1
        conf = row.confidence
        confidence_map[conf] = confidence_map.get(conf, 0) + 1
        if cat == "framework":
            frameworks.append(row.technology.name)

    category_distribution = [CategoryCount(category=c, count=cnt) for c, cnt in sorted(category_map.items())]
    confidence_distribution = [ConfidenceCount(confidence=c, count=cnt) for c, cnt in sorted(confidence_map.items())]

    return TechnologiesSection(
        total_technologies=total,
        category_distribution=category_distribution,
        confidence_distribution=confidence_distribution,
        primary_frameworks=frameworks,
    )


def _build_dependencies_section(db: Session, analysis_id: int) -> DependenciesSection:
    total = repository.count_dependencies(db, analysis_id)
    direct_count, transitive_count = repository.get_dependency_type_counts(db, analysis_id)

    eco_rows = repository.get_ecosystem_breakdown(db, analysis_id)
    ecosystem_breakdown = [EcosystemBreakdown(ecosystem=e, count=cnt) for e, cnt in eco_rows]

    top_rows = repository.get_top_dependencies(db, analysis_id)
    top_packages = [TopPackage(name=d.name, version=d.version, ecosystem=d.ecosystem) for d in top_rows]

    return DependenciesSection(
        total_dependencies=total,
        direct_count=direct_count,
        transitive_count=transitive_count,
        ecosystem_breakdown=ecosystem_breakdown,
        top_packages=top_packages,
    )


def _build_warnings_section(db: Session, analysis_id: int) -> WarningsSection:
    total = repository.count_warnings(db, analysis_id)

    det_rows = repository.get_detector_breakdown(db, analysis_id)
    detector_breakdown = [DetectorCount(detector_name=d, count=cnt) for d, cnt in det_rows]

    return WarningsSection(total_warnings=total, detector_breakdown=detector_breakdown)


_METRIC_KEYS = {
    "project.total_files": "project_total_files",
    "project.total_file_size": "project_total_file_size",
    "languages.count": "language_count",
    "languages.primary": "primary_language",
    "frameworks.count": "framework_count",
    "dependencies.count": "dependency_count",
    "manifests.count": "manifest_count",
}


def _build_metrics_section(db: Session, analysis_id: int) -> MetricsSection:
    rows = repository.list_metrics(db, analysis_id)
    data: dict[str, int] = {}
    for m in rows:
        if m.value is not None:
            data[m.key] = m.value
        elif m.value_str is not None:
            data[m.key] = m.value_str

    return MetricsSection(
        total_metrics=len(rows),
        project_total_files=data.get("project.total_files"),
        project_total_file_size=data.get("project.total_file_size"),
        language_count=data.get("languages.count"),
        primary_language=data.get("languages.primary"),
        framework_count=data.get("frameworks.count"),
        dependency_count=data.get("dependencies.count"),
        manifest_count=data.get("manifests.count"),
    )

import logging
import time

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.modules.analysis import repository
from app.modules.analysis.query_options import (
    DependencyFilter,
    FileFilter,
    QueryOptions,
    WarningFilter,
)

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

logger = logging.getLogger(__name__)


_FILE_SORT_FIELDS = {"relative_path", "file_size", "extension", "language"}
_DEP_SORT_FIELDS = {"name", "ecosystem", "type"}
_WARNING_SORT_FIELDS = {"created_at", "detector_name"}
_ANALYSIS_SORT_FIELDS = {"created_at", "status"}


def _validate_sort(allowed: set[str], sort_by: str) -> str:
    if sort_by not in allowed:
        return next(iter(allowed))
    return sort_by


def _to_paginated_response(page, dto_cls):
    return PaginatedResponse(
        items=[dto_cls.model_validate(item) for item in page.items],
        total=page.total,
        page=page.page,
        size=page.size,
        pages=page.pages,
    )


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


def get_analysis_summary(db: Session, user_id: int, analysis_id: int) -> AnalysisSummaryResponse:
    _start = time.perf_counter()
    analysis = _get_owned_analysis(db, user_id, analysis_id)
    result = AnalysisSummaryResponse(
        analysis_id=analysis.id,
        upload_id=analysis.upload_id,
        status=analysis.status,
        error_detail=analysis.error_detail,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        duration_ms=_duration_ms(analysis),
        file_count=repository.count_analysis_files(db, analysis.id),
        technology_count=len(repository.list_analysis_technologies_with_tech(db, analysis.id)),
        dependency_count=repository.count_dependencies(db, analysis.id),
        metric_count=len(repository.list_metrics(db, analysis.id)),
        warning_count=repository.count_warnings(db, analysis.id),
    )

    _elapsed_ms = (time.perf_counter() - _start) * 1000
    if _elapsed_ms >= settings.SLOW_SERVICE_THRESHOLD_MS:
        logger.warning("get_analysis_summary(%d) took %.0fms", analysis_id, _elapsed_ms)
    else:
        logger.info("get_analysis_summary(%d) took %.0fms", analysis_id, _elapsed_ms)
    return result


def get_analysis_files(
    db: Session,
    user_id: int,
    analysis_id: int,
    page: int = 1,
    size: int = 50,
    extension: str | None = None,
    language: str | None = None,
    is_directory: bool | None = None,
    search: str | None = None,
    sort_by: str = "relative_path",
    sort_dir: str = "asc",
) -> PaginatedResponse[AnalysisFileResponse]:
    _get_owned_analysis(db, user_id, analysis_id)
    sort_by = _validate_sort(_FILE_SORT_FIELDS, sort_by)
    opts = QueryOptions(page=page, size=size, sort_by=sort_by, sort_dir=sort_dir)
    filter = FileFilter(
        extension=extension,
        language=language,
        is_directory=is_directory,
        search=search,
    )
    page_result = repository.list_analysis_files_paginated(db, analysis_id, filter, opts)
    return _to_paginated_response(page_result, AnalysisFileResponse)


def get_analysis_technologies(
    db: Session,
    user_id: int,
    analysis_id: int,
) -> list[AnalysisTechnologyResponse]:
    _get_owned_analysis(db, user_id, analysis_id)
    rows = repository.list_analysis_technologies_with_tech(db, analysis_id)
    return [
        AnalysisTechnologyResponse(
            id=row.id,
            name=row.technology.name,
            category=row.technology.category,
            evidence=row.evidence,
            confidence=row.confidence,
        )
        for row in rows
    ]


def get_analysis_dependencies(
    db: Session,
    user_id: int,
    analysis_id: int,
    page: int = 1,
    size: int = 50,
    ecosystem: str | None = None,
    type: str | None = None,
    search: str | None = None,
    sort_by: str = "name",
    sort_dir: str = "asc",
) -> PaginatedResponse[AnalysisDependencyResponse]:
    _get_owned_analysis(db, user_id, analysis_id)
    sort_by = _validate_sort(_DEP_SORT_FIELDS, sort_by)
    opts = QueryOptions(page=page, size=size, sort_by=sort_by, sort_dir=sort_dir)
    filter = DependencyFilter(ecosystem=ecosystem, type=type, search=search)
    page_result = repository.list_dependencies_paginated(db, analysis_id, filter, opts)
    return PaginatedResponse(
        items=[_to_dep_response(d) for d in page_result.items],
        total=page_result.total,
        page=page_result.page,
        size=page_result.size,
        pages=page_result.pages,
    )


def _to_dep_response(dep) -> AnalysisDependencyResponse:
    return AnalysisDependencyResponse(
        id=dep.id,
        name=dep.name,
        version=dep.version,
        type=dep.type,
        source_files=dep.source_files_list,
        ecosystem=dep.ecosystem,
    )


def get_analysis_metrics(
    db: Session,
    user_id: int,
    analysis_id: int,
) -> list[AnalysisMetricResponse]:
    _get_owned_analysis(db, user_id, analysis_id)
    rows = repository.list_metrics(db, analysis_id)
    return [
        AnalysisMetricResponse(
            id=m.id,
            key=m.key,
            value=m.value if m.value is not None else m.value_str,
        )
        for m in rows
    ]


def get_analysis_warnings(
    db: Session,
    user_id: int,
    analysis_id: int,
    page: int = 1,
    size: int = 50,
    detector_name: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> PaginatedResponse[AnalysisWarningResponse]:
    _get_owned_analysis(db, user_id, analysis_id)
    sort_by = _validate_sort(_WARNING_SORT_FIELDS, sort_by)
    opts = QueryOptions(page=page, size=size, sort_by=sort_by, sort_dir=sort_dir)
    filter = WarningFilter(detector_name=detector_name, search=search)
    page_result = repository.list_warnings_paginated(db, analysis_id, filter, opts)
    return _to_paginated_response(page_result, AnalysisWarningResponse)


def list_project_analyses(
    db: Session,
    user_id: int,
    project_id: int,
    page: int = 1,
    size: int = 20,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> PaginatedResponse[AnalysisListItem]:
    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Project")
    sort_by = _validate_sort(_ANALYSIS_SORT_FIELDS, sort_by)
    opts = QueryOptions(page=page, size=size, sort_by=sort_by, sort_dir=sort_dir)
    page_result = repository.list_analyses_by_project_paginated(db, project_id, opts)
    return PaginatedResponse(
        items=[_to_list_item(a) for a in page_result.items],
        total=page_result.total,
        page=page_result.page,
        size=page_result.size,
        pages=page_result.pages,
    )


def list_upload_analyses(
    db: Session,
    user_id: int,
    upload_id: int,
    page: int = 1,
    size: int = 20,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> PaginatedResponse[AnalysisListItem]:
    from app.modules.uploads import repository as uploads_repository
    upload = uploads_repository.get_upload_by_id(db, upload_id)
    if upload is None:
        raise NotFoundException("Upload")
    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, upload.project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Upload")
    sort_by = _validate_sort(_ANALYSIS_SORT_FIELDS, sort_by)
    opts = QueryOptions(page=page, size=size, sort_by=sort_by, sort_dir=sort_dir)
    page_result = repository.list_analyses_by_upload_paginated(db, upload_id, opts)
    return PaginatedResponse(
        items=[_to_list_item(a) for a in page_result.items],
        total=page_result.total,
        page=page_result.page,
        size=page_result.size,
        pages=page_result.pages,
    )


def _to_list_item(analysis) -> AnalysisListItem:
    return AnalysisListItem(
        id=analysis.id,
        upload_id=analysis.upload_id,
        status=analysis.status,
        error_detail=analysis.error_detail,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
    )

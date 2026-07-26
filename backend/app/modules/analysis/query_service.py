from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.modules.analysis import repository
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
    analysis = _get_owned_analysis(db, user_id, analysis_id)
    return AnalysisSummaryResponse(
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


def get_analysis_files(
    db: Session,
    user_id: int,
    analysis_id: int,
    page: int = 1,
    size: int = 50,
    extension: str | None = None,
    language: str | None = None,
    is_directory: bool | None = None,
    sort_by: str = "relative_path",
    sort_dir: str = "asc",
) -> PaginatedResponse[AnalysisFileResponse]:
    _get_owned_analysis(db, user_id, analysis_id)
    items, total, pages = repository.list_analysis_files_paginated(
        db, analysis_id, page, size, extension, language, is_directory, sort_by, sort_dir,
    )
    return PaginatedResponse(
        items=[AnalysisFileResponse.model_validate(f) for f in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


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
    sort_by: str = "name",
    sort_dir: str = "asc",
) -> PaginatedResponse[AnalysisDependencyResponse]:
    _get_owned_analysis(db, user_id, analysis_id)
    items, total, pages = repository.list_dependencies_paginated(
        db, analysis_id, page, size, ecosystem, type, sort_by, sort_dir,
    )
    return PaginatedResponse(
        items=[_to_dep_response(d) for d in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
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
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> PaginatedResponse[AnalysisWarningResponse]:
    _get_owned_analysis(db, user_id, analysis_id)
    items, total, pages = repository.list_warnings_paginated(
        db, analysis_id, page, size, detector_name, sort_by, sort_dir,
    )
    return PaginatedResponse(
        items=[AnalysisWarningResponse.model_validate(w) for w in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


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
    items, total, pages = repository.list_analyses_by_project_paginated(
        db, project_id, page, size, sort_by, sort_dir,
    )
    return PaginatedResponse(
        items=[_to_list_item(a) for a in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
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
    items, total, pages = repository.list_analyses_by_upload_paginated(
        db, upload_id, page, size, sort_by, sort_dir,
    )
    return PaginatedResponse(
        items=[_to_list_item(a) for a in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
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

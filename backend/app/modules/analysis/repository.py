import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.modules.analysis.query_options import (
    DependencyFilter,
    FileFilter,
    Page,
    QueryOptions,
    WarningFilter,
    apply_sort,
)

from app.models.analysis import Analysis
from app.models.analysis_file import AnalysisFile
from app.models.analysis_technology import AnalysisTechnology
from app.models.analysis_warning import AnalysisWarning
from app.models.dependency import Dependency
from app.models.metric import Metric
from app.models.technology import Technology
from app.models.upload import Upload


def get_analysis_by_id(db: Session, analysis_id: int) -> Analysis | None:
    from sqlalchemy.orm import joinedload
    return (
        db.query(Analysis)
        .options(joinedload(Analysis.upload))
        .filter(Analysis.id == analysis_id)
        .first()
    )


def list_analyses_by_upload(db: Session, upload_id: int) -> list[Analysis]:
    return (
        db.query(Analysis)
        .filter(Analysis.upload_id == upload_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )


def list_analyses_by_project(db: Session, project_id: int) -> list[Analysis]:
    return (
        db.query(Analysis)
        .join(Upload)
        .filter(Upload.project_id == project_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )


def create_analysis(db: Session, data: dict) -> Analysis:
    analysis = Analysis(**data)
    db.add(analysis)
    db.flush()
    db.refresh(analysis)
    return analysis


def set_analysis_status(db: Session, analysis_id: int, status: str) -> Analysis | None:
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis is None:
        return None
    analysis.status = status
    return analysis


def delete_analysis(db: Session, analysis: Analysis) -> None:
    db.delete(analysis)
    db.flush()


def get_technology(db: Session, name: str, category: str) -> Technology | None:
    return (
        db.query(Technology)
        .filter(Technology.name == name, Technology.category == category)
        .first()
    )


def ensure_technology(db: Session, name: str, category: str) -> Technology:
    tech = get_technology(db, name, category)
    if tech is not None:
        return tech
    tech = Technology(name=name, category=category)
    db.add(tech)
    db.flush()
    db.refresh(tech)
    return tech


def list_analysis_technologies(db: Session, analysis_id: int) -> list[AnalysisTechnology]:
    return (
        db.query(AnalysisTechnology)
        .filter(AnalysisTechnology.analysis_id == analysis_id)
        .all()
    )


def add_analysis_technology(
    db: Session, analysis_id: int, technology_id: int,
    evidence: str | None = None, confidence: str = "high",
) -> AnalysisTechnology:
    at = AnalysisTechnology(
        analysis_id=analysis_id,
        technology_id=technology_id,
        evidence=evidence,
        confidence=confidence,
    )
    db.add(at)
    db.flush()
    db.refresh(at)
    return at


def remove_analysis_technology(db: Session, analysis_technology_id: int) -> None:
    at = db.query(AnalysisTechnology).filter(AnalysisTechnology.id == analysis_technology_id).first()
    if at is None:
        return
    db.delete(at)
    db.flush()


def list_analysis_files(db: Session, analysis_id: int) -> list[AnalysisFile]:
    return (
        db.query(AnalysisFile)
        .filter(AnalysisFile.analysis_id == analysis_id)
        .order_by(AnalysisFile.relative_path)
        .all()
    )


def add_analysis_file(db: Session, analysis_id: int, data: dict) -> AnalysisFile:
    af = AnalysisFile(analysis_id=analysis_id, **data)
    db.add(af)
    db.flush()
    db.refresh(af)
    return af


def remove_analysis_file(db: Session, file_id: int) -> None:
    af = db.query(AnalysisFile).filter(AnalysisFile.id == file_id).first()
    if af is None:
        return
    db.delete(af)
    db.flush()


def list_dependencies(db: Session, analysis_id: int) -> list[Dependency]:
    return (
        db.query(Dependency)
        .filter(Dependency.analysis_id == analysis_id)
        .order_by(Dependency.name)
        .all()
    )


def get_dependency(db: Session, dependency_id: int) -> Dependency | None:
    return db.query(Dependency).filter(Dependency.id == dependency_id).first()


def add_dependency(db: Session, analysis_id: int, data: dict) -> Dependency:
    dep = Dependency(analysis_id=analysis_id, **data)
    db.add(dep)
    db.flush()
    db.refresh(dep)
    return dep


def remove_dependency(db: Session, dependency_id: int) -> None:
    dep = db.query(Dependency).filter(Dependency.id == dependency_id).first()
    if dep is None:
        return
    db.delete(dep)
    db.flush()


def get_metric(db: Session, analysis_id: int, key: str) -> Metric | None:
    return (
        db.query(Metric)
        .filter(Metric.analysis_id == analysis_id, Metric.key == key)
        .first()
    )


def set_metric(db: Session, analysis_id: int, key: str, value: int) -> Metric:
    metric = get_metric(db, analysis_id, key)
    if metric is not None:
        metric.value = value
        db.flush()
        db.refresh(metric)
        return metric
    metric = Metric(analysis_id=analysis_id, key=key, value=value)
    db.add(metric)
    db.flush()
    db.refresh(metric)
    return metric


def list_metrics(db: Session, analysis_id: int) -> list[Metric]:
    return (
        db.query(Metric)
        .filter(Metric.analysis_id == analysis_id)
        .order_by(Metric.key)
        .all()
    )


def batch_add_files(db: Session, analysis_id: int, files: list[dict]) -> None:
    for data in files:
        db.add(AnalysisFile(analysis_id=analysis_id, **data))


def batch_add_technologies(
    db: Session, analysis_id: int, technologies: list[dict],
) -> None:
    for data in technologies:
        db.add(AnalysisTechnology(analysis_id=analysis_id, **data))


def batch_add_dependencies(db: Session, analysis_id: int, dependencies: list[dict]) -> None:
    for data in dependencies:
        db.add(Dependency(analysis_id=analysis_id, **data))


def batch_add_metrics(db: Session, analysis_id: int, metrics: list[dict]) -> None:
    for data in metrics:
        db.add(Metric(analysis_id=analysis_id, **data))


def batch_add_warnings(db: Session, analysis_id: int, warnings: list[dict]) -> None:
    for data in warnings:
        db.add(AnalysisWarning(analysis_id=analysis_id, **data))


def update_analysis_status(
    db: Session, analysis_id: int, status: str, error_detail: str | None = None, completed_at: datetime.datetime | None = None,
) -> Analysis | None:
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis is None:
        return None
    analysis.status = status
    if error_detail is not None:
        analysis.error_detail = error_detail
    if completed_at is not None:
        analysis.completed_at = completed_at
    return analysis


# ─── Read-only query helpers ─────────────────────────────────────────


def _paginate(query, page: int, size: int) -> Page:
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return Page(items=items, total=total, page=page, size=size)


def _apply_file_filters(query, filter: FileFilter | None):
    if filter is None:
        return query
    if filter.extension is not None:
        query = query.filter(AnalysisFile.extension == filter.extension)
    if filter.language is not None:
        query = query.filter(AnalysisFile.language == filter.language)
    if filter.is_directory is not None:
        query = query.filter(AnalysisFile.is_directory == filter.is_directory)
    if filter.search is not None:
        pattern = f"%{filter.search}%"
        query = query.filter(
            AnalysisFile.file_name.ilike(pattern)
            | AnalysisFile.relative_path.ilike(pattern)
        )
    return query


def _apply_dependency_filters(query, filter: DependencyFilter | None):
    if filter is None:
        return query
    if filter.ecosystem is not None:
        query = query.filter(Dependency.ecosystem == filter.ecosystem)
    if filter.type is not None:
        query = query.filter(Dependency.type == filter.type)
    if filter.search is not None:
        query = query.filter(Dependency.name.ilike(f"%{filter.search}%"))
    return query


def _apply_warning_filters(query, filter: WarningFilter | None):
    if filter is None:
        return query
    if filter.detector_name is not None:
        query = query.filter(AnalysisWarning.detector_name == filter.detector_name)
    if filter.search is not None:
        query = query.filter(AnalysisWarning.message.ilike(f"%{filter.search}%"))
    return query


_FILE_SORT_FIELDS = {
    "relative_path": AnalysisFile.relative_path,
    "file_size": AnalysisFile.file_size,
    "extension": AnalysisFile.extension,
    "language": AnalysisFile.language,
}

_DEP_SORT_FIELDS = {
    "name": Dependency.name,
    "ecosystem": Dependency.ecosystem,
    "type": Dependency.type,
}

_TECH_SORT_FIELDS = {
    "name": Technology.name,
    "category": Technology.category,
    "confidence": AnalysisTechnology.confidence,
}

_WARNING_SORT_FIELDS = {
    "created_at": AnalysisWarning.created_at,
    "detector_name": AnalysisWarning.detector_name,
}

_ANALYSIS_SORT_FIELDS = {
    "created_at": Analysis.created_at,
    "status": Analysis.status,
}


def list_analysis_files_paginated(
    db: Session,
    analysis_id: int,
    filter: FileFilter | None = None,
    opts: QueryOptions = QueryOptions(),
) -> Page[AnalysisFile]:
    query = db.query(AnalysisFile).filter(AnalysisFile.analysis_id == analysis_id)
    query = _apply_file_filters(query, filter)
    query = apply_sort(query, _FILE_SORT_FIELDS, opts)
    return _paginate(query, opts.page, opts.size)


def count_analysis_files(db: Session, analysis_id: int) -> int:
    return db.query(func.count(AnalysisFile.id)).filter(AnalysisFile.analysis_id == analysis_id).scalar() or 0


def list_analysis_technologies_with_tech(db: Session, analysis_id: int):
    return (
        db.query(AnalysisTechnology)
        .options(joinedload(AnalysisTechnology.technology))
        .filter(AnalysisTechnology.analysis_id == analysis_id)
        .all()
    )


def list_dependencies_paginated(
    db: Session,
    analysis_id: int,
    filter: DependencyFilter | None = None,
    opts: QueryOptions = QueryOptions(),
) -> Page[Dependency]:
    query = db.query(Dependency).filter(Dependency.analysis_id == analysis_id)
    query = _apply_dependency_filters(query, filter)
    query = apply_sort(query, _DEP_SORT_FIELDS, opts)
    return _paginate(query, opts.page, opts.size)


def count_dependencies(db: Session, analysis_id: int) -> int:
    return db.query(func.count(Dependency.id)).filter(Dependency.analysis_id == analysis_id).scalar() or 0


def list_warnings_paginated(
    db: Session,
    analysis_id: int,
    filter: WarningFilter | None = None,
    opts: QueryOptions = QueryOptions(),
) -> Page[AnalysisWarning]:
    query = db.query(AnalysisWarning).filter(AnalysisWarning.analysis_id == analysis_id)
    query = _apply_warning_filters(query, filter)
    query = apply_sort(query, _WARNING_SORT_FIELDS, opts)
    return _paginate(query, opts.page, opts.size)


def count_warnings(db: Session, analysis_id: int) -> int:
    return db.query(func.count(AnalysisWarning.id)).filter(AnalysisWarning.analysis_id == analysis_id).scalar() or 0


def list_analyses_by_project_paginated(
    db: Session,
    project_id: int,
    opts: QueryOptions = QueryOptions(),
) -> Page[Analysis]:
    query = (
        db.query(Analysis)
        .join(Upload)
        .filter(Upload.project_id == project_id)
    )
    query = apply_sort(query, _ANALYSIS_SORT_FIELDS, opts)
    return _paginate(query, opts.page, opts.size)


def list_analyses_by_upload_paginated(
    db: Session,
    upload_id: int,
    opts: QueryOptions = QueryOptions(),
) -> Page[Analysis]:
    query = db.query(Analysis).filter(Analysis.upload_id == upload_id)
    query = apply_sort(query, _ANALYSIS_SORT_FIELDS, opts)
    return _paginate(query, opts.page, opts.size)


# ─── Dashboard aggregation helpers ────────────────────────────────


def get_language_distribution(db: Session, analysis_id: int) -> list[tuple[str, int]]:
    rows = (
        db.query(AnalysisFile.language, func.count(AnalysisFile.id))
        .filter(AnalysisFile.analysis_id == analysis_id, AnalysisFile.language.isnot(None))
        .group_by(AnalysisFile.language)
        .order_by(AnalysisFile.language)
        .all()
    )
    return [(r[0], r[1]) for r in rows]


def get_extension_distribution(db: Session, analysis_id: int) -> list[tuple[str, int]]:
    rows = (
        db.query(AnalysisFile.extension, func.count(AnalysisFile.id))
        .filter(AnalysisFile.analysis_id == analysis_id, AnalysisFile.extension.isnot(None))
        .group_by(AnalysisFile.extension)
        .order_by(AnalysisFile.extension)
        .all()
    )
    return [(r[0], r[1]) for r in rows]


def get_largest_directories(db: Session, analysis_id: int, limit: int = 10) -> list[AnalysisFile]:
    return (
        db.query(AnalysisFile)
        .filter(AnalysisFile.analysis_id == analysis_id, AnalysisFile.is_directory.is_(True))
        .order_by(AnalysisFile.file_size.desc())
        .limit(limit)
        .all()
    )


def get_technology_category_distribution(db: Session, analysis_id: int) -> list[tuple[str, int]]:
    rows = (
        db.query(Technology.category, func.count(AnalysisTechnology.id))
        .join(AnalysisTechnology, AnalysisTechnology.technology_id == Technology.id)
        .filter(AnalysisTechnology.analysis_id == analysis_id)
        .group_by(Technology.category)
        .order_by(Technology.category)
        .all()
    )
    return [(r[0], r[1]) for r in rows]


def get_ecosystem_breakdown(db: Session, analysis_id: int) -> list[tuple[str, int]]:
    rows = (
        db.query(Dependency.ecosystem, func.count(Dependency.id))
        .filter(Dependency.analysis_id == analysis_id, Dependency.ecosystem.isnot(None))
        .group_by(Dependency.ecosystem)
        .order_by(Dependency.ecosystem)
        .all()
    )
    return [(r[0], r[1]) for r in rows]


def get_dependency_type_counts(db: Session, analysis_id: int) -> tuple[int, int]:
    rows = (
        db.query(Dependency.type, func.count(Dependency.id))
        .filter(Dependency.analysis_id == analysis_id)
        .group_by(Dependency.type)
        .all()
    )
    type_map = dict(rows)
    return type_map.get("library", 0), type_map.get("dev", 0)


def get_top_dependencies(db: Session, analysis_id: int, limit: int = 10) -> list[Dependency]:
    return (
        db.query(Dependency)
        .filter(Dependency.analysis_id == analysis_id)
        .order_by(Dependency.name)
        .limit(limit)
        .all()
    )


def get_detector_breakdown(db: Session, analysis_id: int) -> list[tuple[str, int]]:
    rows = (
        db.query(AnalysisWarning.detector_name, func.count(AnalysisWarning.id))
        .filter(AnalysisWarning.analysis_id == analysis_id)
        .group_by(AnalysisWarning.detector_name)
        .order_by(AnalysisWarning.detector_name)
        .all()
    )
    return [(r[0], r[1]) for r in rows]


def count_analysis_directories(db: Session, analysis_id: int) -> int:
    return (
        db.query(func.count(AnalysisFile.id))
        .filter(AnalysisFile.analysis_id == analysis_id, AnalysisFile.is_directory.is_(True))
        .scalar()
        or 0
    )

import datetime
import math

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.analysis import Analysis
from app.models.analysis_file import AnalysisFile
from app.models.analysis_technology import AnalysisTechnology
from app.models.analysis_warning import AnalysisWarning
from app.models.dependency import Dependency
from app.models.metric import Metric
from app.models.technology import Technology
from app.models.upload import Upload


def get_analysis_by_id(db: Session, analysis_id: int) -> Analysis | None:
    return db.query(Analysis).filter(Analysis.id == analysis_id).first()


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
    db.commit()
    db.refresh(analysis)
    return analysis


def set_analysis_status(db: Session, analysis_id: int, status: str) -> Analysis | None:
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis is None:
        return None
    analysis.status = status
    db.commit()
    db.refresh(analysis)
    return analysis


def delete_analysis(db: Session, analysis: Analysis) -> None:
    db.delete(analysis)
    db.commit()


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
    db.commit()
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
    db.commit()
    db.refresh(at)
    return at


def remove_analysis_technology(db: Session, analysis_technology_id: int) -> None:
    at = db.query(AnalysisTechnology).filter(AnalysisTechnology.id == analysis_technology_id).first()
    if at is None:
        return
    db.delete(at)
    db.commit()


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
    db.commit()
    db.refresh(af)
    return af


def remove_analysis_file(db: Session, file_id: int) -> None:
    af = db.query(AnalysisFile).filter(AnalysisFile.id == file_id).first()
    if af is None:
        return
    db.delete(af)
    db.commit()


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
    db.commit()
    db.refresh(dep)
    return dep


def remove_dependency(db: Session, dependency_id: int) -> None:
    dep = db.query(Dependency).filter(Dependency.id == dependency_id).first()
    if dep is None:
        return
    db.delete(dep)
    db.commit()


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
        db.commit()
        db.refresh(metric)
        return metric
    metric = Metric(analysis_id=analysis_id, key=key, value=value)
    db.add(metric)
    db.commit()
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


def _apply_sort(query, model_field_map: dict, sort_by: str, sort_dir: str):
    column = model_field_map.get(sort_by)
    if column is None:
        sort_by = next(iter(model_field_map.keys()))
        column = model_field_map[sort_by]
    if sort_dir == "desc":
        return query.order_by(column.desc())
    return query.order_by(column.asc())


def _paginate(query, page: int, size: int):
    total = query.count()
    pages = max(1, math.ceil(total / size))
    items = query.offset((page - 1) * size).limit(size).all()
    return items, total, pages


def list_analysis_files_paginated(
    db: Session,
    analysis_id: int,
    page: int = 1,
    size: int = 50,
    extension: str | None = None,
    language: str | None = None,
    is_directory: bool | None = None,
    sort_by: str = "relative_path",
    sort_dir: str = "asc",
):
    query = db.query(AnalysisFile).filter(AnalysisFile.analysis_id == analysis_id)
    if extension is not None:
        query = query.filter(AnalysisFile.extension == extension)
    if language is not None:
        query = query.filter(AnalysisFile.language == language)
    if is_directory is not None:
        query = query.filter(AnalysisFile.is_directory == is_directory)
    query = _apply_sort(query, _FILE_SORT_FIELDS, sort_by, sort_dir)
    return _paginate(query, page, size)


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
    page: int = 1,
    size: int = 50,
    ecosystem: str | None = None,
    type: str | None = None,
    sort_by: str = "name",
    sort_dir: str = "asc",
):
    query = db.query(Dependency).filter(Dependency.analysis_id == analysis_id)
    if ecosystem is not None:
        query = query.filter(Dependency.ecosystem == ecosystem)
    if type is not None:
        query = query.filter(Dependency.type == type)
    query = _apply_sort(query, _DEP_SORT_FIELDS, sort_by, sort_dir)
    return _paginate(query, page, size)


def count_dependencies(db: Session, analysis_id: int) -> int:
    return db.query(func.count(Dependency.id)).filter(Dependency.analysis_id == analysis_id).scalar() or 0


def list_warnings_paginated(
    db: Session,
    analysis_id: int,
    page: int = 1,
    size: int = 50,
    detector_name: str | None = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    query = db.query(AnalysisWarning).filter(AnalysisWarning.analysis_id == analysis_id)
    if detector_name is not None:
        query = query.filter(AnalysisWarning.detector_name == detector_name)
    query = _apply_sort(query, _WARNING_SORT_FIELDS, sort_by, sort_dir)
    return _paginate(query, page, size)


def count_warnings(db: Session, analysis_id: int) -> int:
    return db.query(func.count(AnalysisWarning.id)).filter(AnalysisWarning.analysis_id == analysis_id).scalar() or 0


def list_analyses_by_project_paginated(
    db: Session,
    project_id: int,
    page: int = 1,
    size: int = 20,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    query = (
        db.query(Analysis)
        .join(Upload)
        .filter(Upload.project_id == project_id)
    )
    query = _apply_sort(query, _ANALYSIS_SORT_FIELDS, sort_by, sort_dir)
    return _paginate(query, page, size)


def list_analyses_by_upload_paginated(
    db: Session,
    upload_id: int,
    page: int = 1,
    size: int = 20,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    query = db.query(Analysis).filter(Analysis.upload_id == upload_id)
    query = _apply_sort(query, _ANALYSIS_SORT_FIELDS, sort_by, sort_dir)
    return _paginate(query, page, size)

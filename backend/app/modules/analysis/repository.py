from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.analysis_file import AnalysisFile
from app.models.analysis_technology import AnalysisTechnology
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

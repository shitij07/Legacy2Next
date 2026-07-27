from dataclasses import dataclass, asdict
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.models.analysis import Analysis
from app.models.project import Project
from app.models.upload import Upload
from app.modules.analysis import repository as analysis_repository


@dataclass
class SummaryContext:
    project_name: str
    total_files: int
    total_directories: int
    languages: list[dict]
    technologies: list[dict]
    dependencies: list[dict]
    primary_language: str | None
    total_file_size: int
    file_count_by_extension: list[tuple[str, int]]


@dataclass
class FileExplanationContext:
    relative_path: str
    file_name: str
    extension: str | None
    file_size: int
    lines_of_code: int | None
    language: str | None
    content: str


@dataclass
class ModuleFileInfo:
    file_name: str
    extension: str | None
    file_size: int
    lines_of_code: int | None


@dataclass
class ModuleExplanationContext:
    module_path: str
    total_files: int
    total_size: int
    languages: list[str]
    files: list[dict]
    subdirectories: list[str]


@dataclass
class ArchitectureContext:
    project_name: str
    total_files: int
    languages: list[dict]
    technologies: list[dict]
    dependencies: list[dict]
    top_level_directories: list[str]


@dataclass
class TechnicalDebtContext:
    project_name: str
    total_files: int
    total_warnings: int
    detector_breakdown: list[tuple[str, int]]
    warning_samples: list[dict]
    languages: list[str]
    technologies: list[dict]


@dataclass
class ModernizationContext:
    project_name: str
    languages: list[str]
    technologies: list[dict]
    dependencies: list[dict]
    total_dependencies: int
    total_technologies: int
    total_files: int


def _resolve_analysis(db: Session, analysis_id: int) -> Analysis:
    analysis = analysis_repository.get_analysis_by_id(db, analysis_id)
    if analysis is None:
        raise NotFoundException("Analysis")
    return analysis


def _resolve_upload(db: Session, analysis: Analysis) -> Upload:
    upload = db.query(Upload).filter(Upload.id == analysis.upload_id).first()
    if upload is None:
        raise NotFoundException("Upload")
    return upload


def _resolve_project_name(db: Session, analysis: Analysis) -> str:
    upload = _resolve_upload(db, analysis)
    project = db.query(Project).filter(Project.id == upload.project_id).first()
    if project is None:
        return f"Analysis #{analysis.id}"
    return project.name


def _read_file_content(upload: Upload, file_name: str, project_id: int) -> str:
    file_path = Path(settings.UPLOAD_ROOT) / str(project_id) / "files" / upload.stored_name
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8", errors="replace")


def _tech_list(db: Session, analysis_id: int) -> list[dict]:
    return [
        {
            "name": at.technology.name,
            "category": at.technology.category,
            "confidence": at.confidence,
        }
        for at in analysis_repository.list_analysis_technologies_with_tech(db, analysis_id)
    ]


def _dep_list(db: Session, analysis_id: int) -> list[dict]:
    return [
        {
            "name": d.name,
            "version": d.version,
            "ecosystem": d.ecosystem,
        }
        for d in analysis_repository.list_dependencies(db, analysis_id)
    ]


def _lang_list(db: Session, analysis_id: int) -> list[dict]:
    return [
        {"name": name, "count": count}
        for name, count in analysis_repository.get_language_distribution(db, analysis_id)
    ]


def _metric_value(db: Session, analysis_id: int, key: str) -> str | int | None:
    m = analysis_repository.get_metric(db, analysis_id, key)
    if m is None:
        return None
    return m.value if m.value is not None else m.value_str


def _all_files(db: Session, analysis_id: int) -> list[dict]:
    return [
        {
            "relative_path": f.relative_path,
            "file_name": f.file_name,
            "extension": f.extension,
            "file_size": f.file_size,
            "lines_of_code": f.lines_of_code,
            "language": f.language,
            "is_directory": f.is_directory,
        }
        for f in analysis_repository.list_analysis_files(db, analysis_id)
    ]


class ContextBuilder:
    def build_summary_context(self, db: Session, analysis_id: int) -> SummaryContext:
        analysis = _resolve_analysis(db, analysis_id)
        files = _all_files(db, analysis_id)
        techs = _tech_list(db, analysis_id)
        deps = _dep_list(db, analysis_id)
        langs = _lang_list(db, analysis_id)
        primary = _metric_value(db, analysis_id, "primary_language")

        from collections import Counter
        ext_counts = Counter(f.get("extension") or "" for f in files if not f.get("is_directory"))
        ext_sorted = sorted(ext_counts.items(), key=lambda x: (-x[1], x[0]))

        return SummaryContext(
            project_name=_resolve_project_name(db, analysis),
            total_files=sum(1 for f in files if not f.get("is_directory")),
            total_directories=sum(1 for f in files if f.get("is_directory")),
            languages=langs,
            technologies=techs,
            dependencies=deps,
            primary_language=str(primary) if primary else None,
            total_file_size=sum(f.get("file_size", 0) for f in files),
            file_count_by_extension=ext_sorted,
        )

    def build_file_explanation_context(
        self, db: Session, analysis_id: int, file_id: int,
    ) -> FileExplanationContext:
        analysis = _resolve_analysis(db, analysis_id)
        upload = _resolve_upload(db, analysis)
        files = analysis_repository.list_analysis_files(db, analysis_id)
        target = next((f for f in files if f.id == file_id), None)
        if target is None:
            raise NotFoundException("File")
        content = _read_file_content(upload, target.file_name, upload.project_id)
        return FileExplanationContext(
            relative_path=target.relative_path,
            file_name=target.file_name,
            extension=target.extension,
            file_size=target.file_size,
            lines_of_code=target.lines_of_code,
            language=target.language,
            content=content,
        )

    def build_module_explanation_context(
        self, db: Session, analysis_id: int, module_path: str,
    ) -> ModuleExplanationContext:
        analysis = _resolve_analysis(db, analysis_id)
        all_files = _all_files(db, analysis_id)
        prefix = module_path.rstrip("/") + "/"
        matching = [f for f in all_files if f["relative_path"].startswith(prefix) or f["relative_path"] == module_path]
        if not matching:
            raise NotFoundException("Module")

        subdirs = sorted(set(
            p.split("/")[len(module_path.rstrip("/").split("/"))]
            for p in [f["relative_path"] for f in matching]
            if "/" in p[len(prefix) - 1:] if not module_path.endswith("/")
        )) if matching else []

        return ModuleExplanationContext(
            module_path=module_path,
            total_files=sum(1 for f in matching if not f.get("is_directory")),
            total_size=sum(f.get("file_size", 0) for f in matching),
            languages=sorted(set(f["language"] for f in matching if f.get("language"))),
            files=[{"file_name": f["file_name"], "extension": f["extension"], "file_size": f["file_size"], "lines_of_code": f["lines_of_code"]} for f in matching if not f.get("is_directory")],
            subdirectories=subdirs,
        )

    def build_architecture_context(self, db: Session, analysis_id: int) -> ArchitectureContext:
        analysis = _resolve_analysis(db, analysis_id)
        files = _all_files(db, analysis_id)
        techs = _tech_list(db, analysis_id)
        deps = _dep_list(db, analysis_id)
        langs = _lang_list(db, analysis_id)

        top_level = sorted(set(
            f["relative_path"].split("/")[0]
            for f in files if "/" in f["relative_path"]
        ))

        return ArchitectureContext(
            project_name=_resolve_project_name(db, analysis),
            total_files=sum(1 for f in files if not f.get("is_directory")),
            languages=langs,
            technologies=techs,
            dependencies=deps,
            top_level_directories=top_level,
        )

    def build_technical_debt_context(self, db: Session, analysis_id: int) -> TechnicalDebtContext:
        analysis = _resolve_analysis(db, analysis_id)
        files = _all_files(db, analysis_id)
        techs = _tech_list(db, analysis_id)
        warnings = analysis_repository.list_warnings_paginated(db, analysis_id)
        detector_breakdown = analysis_repository.get_detector_breakdown(db, analysis_id)
        total_warnings = analysis_repository.count_warnings(db, analysis_id)
        langs = sorted(set(f.get("language") for f in files if f.get("language")))

        return TechnicalDebtContext(
            project_name=_resolve_project_name(db, analysis),
            total_files=sum(1 for f in files if not f.get("is_directory")),
            total_warnings=total_warnings,
            detector_breakdown=detector_breakdown,
            warning_samples=[{"detector_name": w.detector_name, "message": w.message} for w in warnings.items[:5]] if hasattr(warnings, 'items') else [],
            languages=langs,
            technologies=[{"name": t["name"], "category": t["category"], "confidence": t["confidence"]} for t in techs],
        )

    def build_modernization_context(self, db: Session, analysis_id: int) -> ModernizationContext:
        analysis = _resolve_analysis(db, analysis_id)
        files = _all_files(db, analysis_id)
        techs = _tech_list(db, analysis_id)
        deps = _dep_list(db, analysis_id)
        langs = sorted(set(f.get("language") for f in files if f.get("language")))

        return ModernizationContext(
            project_name=_resolve_project_name(db, analysis),
            languages=langs,
            technologies=[{"name": t["name"], "category": t["category"], "confidence": t["confidence"]} for t in techs],
            dependencies=deps,
            total_dependencies=analysis_repository.count_dependencies(db, analysis_id),
            total_technologies=len(techs),
            total_files=sum(1 for f in files if not f.get("is_directory")),
        )

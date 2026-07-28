import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ValidationException
from app.models.report import Report, ReportFormat, ReportStatus
from app.modules.reports import repository as reports_repository
from app.modules.reports.schemas import ReportResponse

logger = logging.getLogger(__name__)


def _get_owned_project(db: Session, user_id: int, project_id: int):
    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Project")
    return project


def _get_owned_analysis(db: Session, user_id: int, analysis_id: int):
    from app.modules.analysis import repository as analysis_repository
    analysis = analysis_repository.get_analysis_by_id(db, analysis_id)
    if analysis is None:
        raise NotFoundException("Analysis")
    upload = analysis.upload
    if upload is None:
        raise NotFoundException("Analysis")
    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, upload.project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Analysis")
    return analysis, project


def _collect_analysis_data(db: Session, analysis_id: int) -> dict:
    from app.modules.analysis import repository as analysis_repository
    from app.modules.analysis.schemas import (
        AnalysisDependencyResponse,
        AnalysisFileResponse,
        AnalysisMetricResponse,
        AnalysisTechnologyResponse,
        AnalysisWarningResponse,
    )

    analysis = analysis_repository.get_analysis_by_id(db, analysis_id)
    if analysis is None:
        return {}

    files = analysis_repository.list_analysis_files(db, analysis_id)
    technologies_rows = analysis_repository.list_analysis_technologies_with_tech(db, analysis_id)
    dependencies = analysis_repository.list_dependencies(db, analysis_id)
    metrics = analysis_repository.list_metrics(db, analysis_id)
    warnings = analysis_repository.list_warnings_paginated(db, analysis_id)

    return {
        "analysis": analysis,
        "files": [AnalysisFileResponse.model_validate(f) for f in files],
        "technologies": [
            AnalysisTechnologyResponse(
                id=row.id,
                name=row.technology.name,
                category=row.technology.category,
                evidence=row.evidence,
                confidence=row.confidence,
            )
            for row in technologies_rows
        ],
        "dependencies": [
            AnalysisDependencyResponse(
                id=d.id,
                name=d.name,
                version=d.version,
                type=d.type,
                source_files=d.source_files_list,
                ecosystem=d.ecosystem,
            )
            for d in dependencies
        ],
        "metrics": [
            AnalysisMetricResponse(
                id=m.id,
                key=m.key,
                value=m.value if m.value is not None else m.value_str,
            )
            for m in metrics
        ],
        "warnings": [
            AnalysisWarningResponse(
                id=w.id,
                detector_name=w.detector_name,
                message=w.message,
                created_at=w.created_at,
            )
            for w in warnings.items
        ],
    }


def _collect_ai_outputs(db: Session, analysis_id: int, user_id: int) -> dict:
    outputs = {}
    try:
        from app.modules.ai.service import DefaultAIService
        from app.modules.ai.context_builder import ContextBuilder
        from app.modules.ai.prompt_loader import PromptLoader
        from app.integrations.ai.provider import LiteLLMProvider
        from app.core.config import settings

        provider = LiteLLMProvider(
            model=settings.AI_MODEL,
            api_key=settings.AI_API_KEY,
            temperature=settings.AI_TEMPERATURE,
            max_tokens=settings.AI_MAX_TOKENS,
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        ai_service = DefaultAIService(
            provider=provider,
            context_builder=ContextBuilder(),
            prompt_loader=PromptLoader(),
        )

        outputs["summary"] = ai_service.generate_summary(db, user_id, analysis_id).content
        outputs["architecture"] = ai_service.generate_architecture(db, user_id, analysis_id).content
        outputs["technical_debt"] = ai_service.generate_technical_debt(db, user_id, analysis_id).content
        outputs["modernization"] = ai_service.generate_modernization(db, user_id, analysis_id).content
    except Exception as e:
        logger.warning("AI generation failed for report (analysis=%d): %s", analysis_id, e)
    return outputs


def _generate_markdown(data: dict, ai_outputs: dict, project_name: str) -> str:
    analysis = data.get("analysis")
    files = data.get("files", [])
    technologies = data.get("technologies", [])
    dependencies = data.get("dependencies", [])
    metrics = data.get("metrics", [])
    warnings = data.get("warnings", [])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = []
    lines.append(f"# Analysis Report: {project_name}")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append("")

    if analysis:
        lines.append("## Project Information")
        lines.append("")
        lines.append(f"- **Analysis ID:** {analysis.id}")
        lines.append(f"- **Status:** {analysis.status}")
        lines.append(f"- **Created:** {analysis.created_at}")
        if analysis.completed_at:
            lines.append(f"- **Completed:** {analysis.completed_at}")
        if analysis.error_detail:
            lines.append(f"- **Error:** {analysis.error_detail}")
        lines.append("")

    lines.append("## Analysis Summary")
    lines.append("")
    lines.append(f"- **Total Files:** {len(files)}")
    lines.append(f"- **Technologies:** {len(technologies)}")
    lines.append(f"- **Dependencies:** {len(dependencies)}")
    lines.append(f"- **Metrics:** {len(metrics)}")
    lines.append(f"- **Warnings:** {len(warnings)}")
    lines.append("")

    if files:
        lines.append("## Files Overview")
        lines.append("")
        lines.append("| File | Extension | Language | Size |")
        lines.append("|------|-----------|----------|------|")
        for f in files:
            ext = f.extension or ""
            lang = f.language or ""
            lines.append(f"| {f.relative_path} | {ext} | {lang} | {f.file_size} |")
        lines.append("")

    if technologies:
        lines.append("## Technology Stack")
        lines.append("")
        lines.append("| Technology | Category | Confidence |")
        lines.append("|------------|----------|------------|")
        for t in technologies:
            lines.append(f"| {t.name} | {t.category} | {t.confidence} |")
        lines.append("")

    if dependencies:
        lines.append("## Dependencies")
        lines.append("")
        lines.append("| Package | Version | Ecosystem | Type |")
        lines.append("|---------|---------|-----------|------|")
        for d in dependencies:
            ver = d.version or ""
            eco = d.ecosystem or ""
            lines.append(f"| {d.name} | {ver} | {eco} | {d.type} |")
        lines.append("")

    if warnings:
        lines.append("## Warnings")
        lines.append("")
        lines.append("| Detector | Message |")
        lines.append("|----------|---------|")
        for w in warnings:
            lines.append(f"| {w.detector_name} | {w.message} |")
        lines.append("")

    if metrics:
        lines.append("## Metrics")
        lines.append("")
        lines.append("| Key | Value |")
        lines.append("|-----|-------|")
        for m in metrics:
            lines.append(f"| {m.key} | {m.value} |")
        lines.append("")

    if ai_outputs.get("summary"):
        lines.append("---")
        lines.append("## AI Summary")
        lines.append("")
        lines.append(ai_outputs["summary"])
        lines.append("")

    if ai_outputs.get("architecture"):
        lines.append("---")
        lines.append("## Architecture")
        lines.append("")
        lines.append(ai_outputs["architecture"])
        lines.append("")

    if ai_outputs.get("technical_debt"):
        lines.append("---")
        lines.append("## Technical Debt")
        lines.append("")
        lines.append(ai_outputs["technical_debt"])
        lines.append("")

    if ai_outputs.get("modernization"):
        lines.append("---")
        lines.append("## Modernization Recommendations")
        lines.append("")
        lines.append(ai_outputs["modernization"])
        lines.append("")

    lines.append("---")
    lines.append(f"*Report generated by Legacy2Next at {now}*")
    lines.append("")

    return "\n".join(lines)


def _generate_json(data: dict, ai_outputs: dict, project_name: str) -> str:
    import json

    analysis = data.get("analysis")
    files = data.get("files", [])
    technologies = data.get("technologies", [])
    dependencies = data.get("dependencies", [])
    metrics = data.get("metrics", [])
    warnings = data.get("warnings", [])
    now = datetime.now(timezone.utc).isoformat()

    report_data = {
        "report": {
            "title": f"Analysis Report: {project_name}",
            "generated_at": now,
            "project": project_name,
        },
        "analysis_summary": {
            "total_files": len(files),
            "total_technologies": len(technologies),
            "total_dependencies": len(dependencies),
            "total_metrics": len(metrics),
            "total_warnings": len(warnings),
        },
        "files": [
            {
                "path": f.relative_path,
                "extension": f.extension,
                "language": f.language,
                "size": f.file_size,
            }
            for f in files
        ],
        "technologies": [
            {
                "name": t.name,
                "category": t.category,
                "confidence": t.confidence,
            }
            for t in technologies
        ],
        "dependencies": [
            {
                "name": d.name,
                "version": d.version,
                "ecosystem": d.ecosystem,
                "type": d.type,
            }
            for d in dependencies
        ],
        "metrics": [
            {
                "key": m.key,
                "value": m.value,
            }
            for m in metrics
        ],
        "warnings": [
            {
                "detector": w.detector_name,
                "message": w.message,
            }
            for w in warnings
        ],
    }

    if ai_outputs:
        report_data["ai_insights"] = {}
        if ai_outputs.get("summary"):
            report_data["ai_insights"]["summary"] = ai_outputs["summary"]
        if ai_outputs.get("architecture"):
            report_data["ai_insights"]["architecture"] = ai_outputs["architecture"]
        if ai_outputs.get("technical_debt"):
            report_data["ai_insights"]["technical_debt"] = ai_outputs["technical_debt"]
        if ai_outputs.get("modernization"):
            report_data["ai_insights"]["modernization"] = ai_outputs["modernization"]

    return json.dumps(report_data, indent=2)


def generate_report(
    db: Session,
    user_id: int,
    project_id: int,
    analysis_id: int,
    title: str,
    report_format: ReportFormat,
) -> ReportResponse:
    project = _get_owned_project(db, user_id, project_id)
    _get_owned_analysis(db, user_id, analysis_id)

    report_data = {
        "project_id": project_id,
        "analysis_id": analysis_id,
        "user_id": user_id,
        "title": title,
        "format": report_format,
        "status": ReportStatus.GENERATING,
    }
    report = reports_repository.create_report(db, report_data)

    try:
        data = _collect_analysis_data(db, analysis_id)
        ai_outputs = _collect_ai_outputs(db, analysis_id, user_id)

        if report_format == ReportFormat.MARKDOWN:
            content = _generate_markdown(data, ai_outputs, project.name)
        elif report_format == ReportFormat.JSON:
            content = _generate_json(data, ai_outputs, project.name)
        else:
            raise ValidationException(f"Unsupported report format: {report_format}")

        report = reports_repository.update_report(
            db, report,
            {"status": ReportStatus.READY, "content": content},
        )
    except Exception as e:
        logger.error("Report generation failed: %s", e)
        report = reports_repository.update_report(
            db, report,
            {"status": ReportStatus.FAILED},
        )

    db.commit()
    return ReportResponse.model_validate(report)


def list_reports(
    db: Session,
    user_id: int,
    project_id: int,
    *,
    analysis_id: int | None = None,
    status: str | None = None,
    format: str | None = None,
    page: int = 1,
    size: int = 20,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    project = _get_owned_project(db, user_id, project_id)

    from app.models.report import ReportFormat, ReportStatus
    fmt_enum = None
    if format is not None:
        fmt_enum = ReportFormat(format)
    status_enum = None
    if status is not None:
        status_enum = ReportStatus(status)

    page_result = reports_repository.list_reports(
        db,
        project_id=project_id,
        analysis_id=analysis_id,
        status=status_enum,
        format=fmt_enum,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

    from app.modules.reports.schemas import ReportSummary, ReportListResponse
    return ReportListResponse(
        items=[ReportSummary.model_validate(r) for r in page_result.items],
        total=page_result.total,
        page=page_result.page,
        size=page_result.size,
        pages=page_result.pages,
    )


def get_report(db: Session, user_id: int, report_id: int) -> ReportResponse:
    report = reports_repository.get_report(db, report_id)
    if report is None:
        raise NotFoundException("Report")

    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, report.project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Report")

    return ReportResponse.model_validate(report)


def delete_report(db: Session, user_id: int, report_id: int) -> None:
    report = reports_repository.get_report(db, report_id)
    if report is None:
        raise NotFoundException("Report")

    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, report.project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Report")

    reports_repository.delete_report(db, report)
    db.commit()

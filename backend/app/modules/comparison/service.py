import json
import logging

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ValidationException
from app.models.comparison import Comparison
from app.modules.comparison import repository as comparison_repository
from app.modules.comparison.schemas import (
    ComparisonData,
    ComparisonListResponse,
    ComparisonResponse,
    ComparisonSummary,
    DependencyComparison,
    FileComparison,
    MetricDiff,
    MetricsComparison,
    TechnologyComparison,
    WarningComparison,
)

logger = logging.getLogger(__name__)


def _get_owned_project(db: Session, user_id: int, project_id: int):
    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Project")
    return project


def _get_analysis_data_for_comparison(db: Session, analysis_id: int) -> dict:
    from app.modules.analysis import repository as analysis_repository
    analysis = analysis_repository.get_analysis_by_id(db, analysis_id)
    if analysis is None:
        return {}

    files_raw = analysis_repository.list_analysis_files(db, analysis_id)
    tech_rows = analysis_repository.list_analysis_technologies_with_tech(db, analysis_id)
    deps_raw = analysis_repository.list_dependencies(db, analysis_id)
    metrics_raw = analysis_repository.list_metrics(db, analysis_id)
    warnings_page = analysis_repository.list_warnings_paginated(db, analysis_id)

    technologies = []
    for row in tech_rows:
        technologies.append({
            "id": row.id,
            "name": row.technology.name,
            "category": row.technology.category,
            "evidence": row.evidence,
            "confidence": row.confidence,
        })

    dependencies = []
    for d in deps_raw:
        dependencies.append({
            "id": d.id,
            "name": d.name,
            "version": d.version,
            "type": d.type,
            "source_files": d.source_files_list,
            "ecosystem": d.ecosystem,
        })

    files = []
    for f in files_raw:
        files.append({
            "id": f.id,
            "relative_path": f.relative_path,
            "file_name": f.file_name,
            "extension": f.extension,
            "file_size": f.file_size,
            "lines_of_code": f.lines_of_code,
            "language": f.language,
        })

    metrics = {}
    for m in metrics_raw:
        metrics[m.key] = m.value if m.value is not None else m.value_str

    warnings = []
    for w in warnings_page.items:
        warnings.append({
            "id": w.id,
            "detector_name": w.detector_name,
            "message": w.message,
        })

    return {
        "analysis": analysis,
        "technologies": technologies,
        "dependencies": dependencies,
        "files": files,
        "metrics": metrics,
        "warnings": warnings,
    }


def _compare_technologies(data_a: dict, data_b: dict) -> TechnologyComparison:
    techs_a = {(t["name"], t["category"]) for t in data_a.get("technologies", [])}
    techs_b = {(t["name"], t["category"]) for t in data_b.get("technologies", [])}

    tech_map_a = {(t["name"], t["category"]): t for t in data_a.get("technologies", [])}
    tech_map_b = {(t["name"], t["category"]): t for t in data_b.get("technologies", [])}

    added_names = techs_b - techs_a
    removed_names = techs_a - techs_b
    common_names = techs_a & techs_b

    added = [tech_map_b[n] for n in added_names]
    removed = [tech_map_a[n] for n in removed_names]
    common = [tech_map_a[n] for n in common_names]

    version_changes = []
    for name_key in common_names:
        t_a = tech_map_a[name_key]
        t_b = tech_map_b[name_key]
        if t_a.get("evidence") != t_b.get("evidence") or t_a.get("confidence") != t_b.get("confidence"):
            version_changes.append({"name": name_key[0], "category": name_key[1], "from": t_a, "to": t_b})

    return TechnologyComparison(added=added, removed=removed, common=common, version_changes=version_changes)


def _compare_dependencies(data_a: dict, data_b: dict) -> DependencyComparison:
    deps_a = {(d["name"], d.get("ecosystem")): d for d in data_a.get("dependencies", [])}
    deps_b = {(d["name"], d.get("ecosystem")): d for d in data_b.get("dependencies", [])}

    keys_a = set(deps_a.keys())
    keys_b = set(deps_b.keys())

    added_keys = keys_b - keys_a
    removed_keys = keys_a - keys_b
    common_keys = keys_a & keys_b

    added = [deps_b[k] for k in added_keys]
    removed = [deps_a[k] for k in removed_keys]
    updated = []
    for k in common_keys:
        if deps_a[k].get("version") != deps_b[k].get("version"):
            updated.append({"name": k[0], "ecosystem": k[1], "from": deps_a[k], "to": deps_b[k]})

    return DependencyComparison(added=added, removed=removed, updated=updated)


def _compare_files(data_a: dict, data_b: dict) -> FileComparison:
    files_a = {f["relative_path"]: f for f in data_a.get("files", [])}
    files_b = {f["relative_path"]: f for f in data_b.get("files", [])}

    paths_a = set(files_a.keys())
    paths_b = set(files_b.keys())

    added_paths = paths_b - paths_a
    removed_paths = paths_a - paths_b
    common_paths = paths_a & paths_b

    added = [files_b[p] for p in added_paths]
    removed = [files_a[p] for p in removed_paths]
    modified = []
    for p in common_paths:
        if files_a[p].get("file_size") != files_b[p].get("file_size") or files_a[p].get("lines_of_code") != files_b[p].get("lines_of_code"):
            modified.append({"path": p, "from": files_a[p], "to": files_b[p]})

    return FileComparison(
        added=added, removed=removed, modified=modified,
        total_a=len(files_a), total_b=len(files_b),
    )


def _compare_warnings(data_a: dict, data_b: dict) -> WarningComparison:
    warnings_a = {(w["detector_name"], w["message"]) for w in data_a.get("warnings", [])}
    warnings_b = {(w["detector_name"], w["message"]) for w in data_b.get("warnings", [])}

    warning_map_a = {(w["detector_name"], w["message"]): w for w in data_a.get("warnings", [])}
    warning_map_b = {(w["detector_name"], w["message"]): w for w in data_b.get("warnings", [])}

    added_set = warnings_b - warnings_a
    resolved_set = warnings_a - warnings_b
    persistent_set = warnings_a & warnings_b

    added = [warning_map_b[w] for w in added_set]
    resolved = [warning_map_a[w] for w in resolved_set]
    persistent = [warning_map_a[w] for w in persistent_set]
    delta = len(added) - len(resolved)

    return WarningComparison(added=added, resolved=resolved, persistent=persistent, delta=delta)


def _compare_metrics(data_a: dict, data_b: dict) -> MetricsComparison:
    metrics_a = data_a.get("metrics", {})
    metrics_b = data_b.get("metrics", {})

    def _int_val(v):
        if v is None:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    def _metric_diff(key: str) -> MetricDiff | None:
        va = _int_val(metrics_a.get(key))
        vb = _int_val(metrics_b.get(key))
        if va is None and vb is None:
            return None
        abs_diff = None
        pct_diff = None
        if va is not None and vb is not None:
            abs_diff = vb - va
            if va != 0:
                pct_diff = round((abs_diff / abs(va)) * 100, 1)
        return MetricDiff(key=key, a_value=va, b_value=vb, abs_diff=abs_diff, pct_diff=pct_diff)

    return MetricsComparison(
        loc=_metric_diff("loc") or _metric_diff("lines_of_code") or _metric_diff("total_lines"),
        file_count=_metric_diff("file_count") or _metric_diff("total_files") or _metric_diff("files"),
        dependency_count=_metric_diff("dependency_count") or _metric_diff("total_dependencies") or _metric_diff("dependencies"),
        technology_count=_metric_diff("technology_count") or _metric_diff("total_technologies") or _metric_diff("technologies"),
        warning_count=_metric_diff("warning_count") or _metric_diff("total_warnings") or _metric_diff("warnings"),
    )


def _generate_summary(comparison_data: ComparisonData) -> str:
    parts = []
    tech = comparison_data.technologies
    deps = comparison_data.dependencies
    files = comparison_data.files
    warnings_c = comparison_data.warnings
    metrics = comparison_data.metrics

    if tech.added:
        names = [t["name"] for t in tech.added[:3]]
        parts.append(f"added {', '.join(names)}{' +more' if len(tech.added) > 3 else ''}")
    if tech.removed:
        names = [t["name"] for t in tech.removed[:3]]
        parts.append(f"removed {', '.join(names)}{' +more' if len(tech.removed) > 3 else ''}")

    if deps.added:
        parts.append(f"introduced {len(deps.added)} new {'dependency' if len(deps.added) == 1 else 'dependencies'}")
    if deps.removed:
        parts.append(f"removed {len(deps.removed)} {'dependency' if len(deps.removed) == 1 else 'dependencies'}")
    if deps.updated:
        parts.append(f"updated {len(deps.updated)} {'dependency' if len(deps.updated) == 1 else 'dependencies'}")

    if files.added:
        parts.append(f"added {len(files.added)} {'file' if len(files.added) == 1 else 'files'}")
    if files.removed:
        parts.append(f"removed {len(files.removed)} {'file' if len(files.removed) == 1 else 'files'}")

    delta = warnings_c.delta
    if delta > 0:
        parts.append(f"introduced {delta} new {'warning' if delta == 1 else 'warnings'}")
    elif delta < 0:
        parts.append(f"resolved {abs(delta)} {'warning' if abs(delta) == 1 else 'warnings'}")
    if not warnings_c.persistent and (warnings_c.added or warnings_c.resolved):
        parts.append("with no persistent warnings")

    for metric_name, metric_val in [
        ("lines of code", metrics.loc),
        ("file count", metrics.file_count),
    ]:
        if metric_val and metric_val.abs_diff is not None:
            direction = "increased" if metric_val.abs_diff > 0 else "decreased"
            parts.append(f"{metric_name} {direction} by {abs(metric_val.abs_diff)} ({metric_val.pct_diff}%)")

    if not parts:
        return "No significant differences detected between the two analyses."

    return "This project " + ", ".join(parts[:-1]) + (", and " if len(parts) > 1 else "") + parts[-1] + "."


def generate_comparison(
    db: Session,
    user_id: int,
    project_id: int,
    analysis_a_id: int,
    analysis_b_id: int,
) -> ComparisonResponse:
    if analysis_a_id == analysis_b_id:
        raise ValidationException("Cannot compare an analysis with itself")

    project = _get_owned_project(db, user_id, project_id)

    from app.modules.analysis import repository as analysis_repository
    analysis_a = analysis_repository.get_analysis_by_id(db, analysis_a_id)
    if analysis_a is None:
        raise NotFoundException("Analysis A")

    analysis_b = analysis_repository.get_analysis_by_id(db, analysis_b_id)
    if analysis_b is None:
        raise NotFoundException("Analysis B")

    upload_a = analysis_a.upload
    upload_b = analysis_b.upload
    if upload_a is None or upload_b is None:
        raise NotFoundException("Analysis")
    if upload_a.project_id != project_id or upload_b.project_id != project_id:
        raise ValidationException("Both analyses must belong to the same project")

    data_a = _get_analysis_data_for_comparison(db, analysis_a_id)
    data_b = _get_analysis_data_for_comparison(db, analysis_b_id)

    comparison_data = ComparisonData(
        technologies=_compare_technologies(data_a, data_b),
        dependencies=_compare_dependencies(data_a, data_b),
        files=_compare_files(data_a, data_b),
        warnings=_compare_warnings(data_a, data_b),
        metrics=_compare_metrics(data_a, data_b),
    )

    summary = _generate_summary(comparison_data)

    comparison = comparison_repository.create_comparison(db, {
        "project_id": project_id,
        "analysis_a_id": analysis_a_id,
        "analysis_b_id": analysis_b_id,
        "summary": summary,
        "comparison_data": comparison_data.model_dump_json(),
    })

    db.commit()

    return ComparisonResponse(
        id=comparison.id,
        project_id=comparison.project_id,
        analysis_a_id=comparison.analysis_a_id,
        analysis_b_id=comparison.analysis_b_id,
        summary=comparison.summary,
        comparison_data=comparison_data,
        created_at=comparison.created_at,
    )


def get_comparison(db: Session, user_id: int, comparison_id: int) -> ComparisonResponse:
    comparison = comparison_repository.get_comparison(db, comparison_id)
    if comparison is None:
        raise NotFoundException("Comparison")

    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, comparison.project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Comparison")

    comparison_data = None
    if comparison.comparison_data:
        try:
            raw = json.loads(comparison.comparison_data)
            comparison_data = ComparisonData.model_validate(raw)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Failed to parse comparison_data for %d: %s", comparison_id, e)

    return ComparisonResponse(
        id=comparison.id,
        project_id=comparison.project_id,
        analysis_a_id=comparison.analysis_a_id,
        analysis_b_id=comparison.analysis_b_id,
        summary=comparison.summary,
        comparison_data=comparison_data,
        created_at=comparison.created_at,
    )


def list_comparisons(
    db: Session,
    user_id: int,
    project_id: int,
    *,
    page: int = 1,
    size: int = 20,
) -> ComparisonListResponse:
    _get_owned_project(db, user_id, project_id)

    page_result = comparison_repository.list_comparisons(
        db,
        project_id=project_id,
        page=page,
        size=size,
    )

    return ComparisonListResponse(
        items=[ComparisonSummary.model_validate(r) for r in page_result.items],
        total=page_result.total,
        page=page_result.page,
        size=page_result.size,
        pages=page_result.pages,
    )


def delete_comparison(db: Session, user_id: int, comparison_id: int) -> None:
    comparison = comparison_repository.get_comparison(db, comparison_id)
    if comparison is None:
        raise NotFoundException("Comparison")

    from app.modules.projects import repository as projects_repository
    project = projects_repository.get_project_by_id(db, comparison.project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Comparison")

    comparison_repository.delete_comparison(db, comparison)
    db.commit()

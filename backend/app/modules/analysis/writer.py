import dataclasses
import datetime
import json
from typing import Any

from sqlalchemy.orm import Session

from app.modules.analysis.types import AnalysisResults
from app.modules.analysis import repository


@dataclasses.dataclass(frozen=True)
class PersistenceResult:
    analysis_id: int
    file_count: int
    technology_count: int
    dependency_count: int
    metric_count: int
    warning_count: int
    error_detail: str | None


class AnalysisWriter:

    def write(
        self,
        db: Session,
        analysis_id: int,
        results: AnalysisResults,
    ) -> PersistenceResult:
        file_count = self._write_files(db, analysis_id, results)
        technology_count = self._write_technologies(db, analysis_id, results)
        dependency_count = self._write_dependencies(db, analysis_id, results)
        metric_count = self._write_metrics(db, analysis_id, results)
        warning_count = self._write_warnings(db, analysis_id, results)
        error_detail = self._build_error_detail(results)
        self._update_status(db, analysis_id, results, error_detail)

        return PersistenceResult(
            analysis_id=analysis_id,
            file_count=file_count,
            technology_count=technology_count,
            dependency_count=dependency_count,
            metric_count=metric_count,
            warning_count=warning_count,
            error_detail=error_detail,
        )

    def _write_files(self, db: Session, analysis_id: int, results: AnalysisResults) -> int:
        records = [
            {
                "relative_path": f.relative_path,
                "file_name": f.file_name,
                "extension": f.extension,
                "file_size": f.file_size,
                "language": f.language,
            }
            for f in results.all_files
        ]
        if not records:
            return 0
        repository.batch_add_files(db, analysis_id, records)
        return len(records)

    def _write_technologies(self, db: Session, analysis_id: int, results: AnalysisResults) -> int:
        technology_index: dict[tuple[str, str], int] = {}
        analysis_techs: list[dict[str, Any]] = []
        for tech in results.all_technologies:
            key = (tech.name, tech.category)
            if key not in technology_index:
                row = repository.ensure_technology(db, tech.name, tech.category)
                technology_index[key] = row.id
            analysis_techs.append({
                "technology_id": technology_index[key],
                "evidence": tech.evidence,
                "confidence": tech.confidence,
            })
        if not analysis_techs:
            return 0
        repository.batch_add_technologies(db, analysis_id, analysis_techs)
        return len(analysis_techs)

    def _write_dependencies(self, db: Session, analysis_id: int, results: AnalysisResults) -> int:
        records: list[dict[str, Any]] = []
        seen: set[tuple[str, str | None]] = set()
        for dep in results.all_dependencies:
            key = (dep.name, dep.ecosystem or "unknown")
            if key in seen:
                continue
            seen.add(key)
            records.append({
                "name": dep.name,
                "version": dep.version,
                "type": dep.type,
                "source_file": dep.source_files[0] if dep.source_files else None,
                "source_files": json.dumps(list(dep.source_files)) if dep.source_files else None,
                "ecosystem": dep.ecosystem,
            })
        if not records:
            return 0
        repository.batch_add_dependencies(db, analysis_id, records)
        return len(records)

    def _write_metrics(self, db: Session, analysis_id: int, results: AnalysisResults) -> int:
        records: list[dict[str, Any]] = []
        seen_keys: set[str] = set()
        for metric in results.all_metrics:
            if metric.key in seen_keys:
                continue
            seen_keys.add(metric.key)
            if isinstance(metric.value, int):
                records.append({
                    "key": metric.key,
                    "value": metric.value,
                    "value_str": None,
                })
            else:
                records.append({
                    "key": metric.key,
                    "value": None,
                    "value_str": metric.value,
                })
        if not records:
            return 0
        repository.batch_add_metrics(db, analysis_id, records)
        return len(records)

    def _write_warnings(self, db: Session, analysis_id: int, results: AnalysisResults) -> int:
        records: list[dict[str, Any]] = []
        for r in results.results:
            for w in r.warnings:
                records.append({
                    "detector_name": w.detector_name,
                    "message": w.message,
                })
        if not records:
            return 0
        repository.batch_add_warnings(db, analysis_id, records)
        return len(records)

    def _build_error_detail(self, results: AnalysisResults) -> str | None:
        errors: list[tuple[str, str]] = []
        for r in results.results:
            if r.error is not None:
                errors.append((r.detector_name, r.error))
        if not errors:
            return None
        errors.sort(key=lambda x: x[0])
        return "; ".join(f"{name}: {msg}" for name, msg in errors)

    def _update_status(
        self,
        db: Session,
        analysis_id: int,
        results: AnalysisResults,
        error_detail: str | None,
    ) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)
        if error_detail is not None:
            repository.update_analysis_status(
                db,
                analysis_id=analysis_id,
                status="COMPLETED_WITH_ERRORS",
                error_detail=error_detail,
                completed_at=now,
            )
        else:
            repository.update_analysis_status(
                db,
                analysis_id=analysis_id,
                status="COMPLETED",
                completed_at=now,
            )

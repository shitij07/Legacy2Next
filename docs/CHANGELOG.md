# Changelog

## 2026-07-26 — M4.6B MetricsCollector

### Added
- `backend/app/modules/analysis/metrics_collector.py` — `MetricsCollector` class with pure aggregation of project metrics from `AnalysisResults`:
  - `project.total_files`, `project.total_file_size`
  - `languages.count`, `languages.primary`
  - `frameworks.count`
  - `dependencies.count`, `dependencies.<ecosystem>` (dynamic, alphabetically sorted)
  - `manifests.count`
- `backend/app/modules/analysis/metric_keys.py` — `MetricKey(StrEnum)` with stable constants for all fixed metric keys
- `backend/tests/test_analysis/test_metrics_collector.py` — 51 tests across 14 test classes covering all metrics, edge cases, determinism, and result integrity

### Changed
- `backend/app/modules/analysis/types.py` — `DetectedMetric.value` widened from `int` to `int | str` to support string-valued metrics (e.g., `languages.primary`)
- `docs/ARCHITECTURE.md` — Added MetricsCollector aggregation stage documentation, updated analysis module status
- `docs/Legacy2Next_PROJECT_STATE.md` — Updated metrics collector progress, next tasks, test counts

### Architecture
- MetricsCollector reads `AnalysisResults` only — no `DiscoveryContext`, no file I/O, no network, no parsing
- Deterministic output: stable metric ordering, alphabetically sorted ecosystems, identical results for identical input
- O(n) in detector output size — each result visited once

## 2026-07-26 — M4.7B AnalysisPipeline

### Added
- `backend/app/modules/analysis/pipeline.py` — `AnalysisPipeline` class orchestrating the full analysis workflow:
  - `DiscoveryEngine.discover()` → detectors (Language, Framework, Dependency) → `MetricsCollector`
  - Constructor injection: `engine`, `detectors`, `metrics_collector`
  - Sequential execution, deterministic output, timing recorded
  - Failure isolation: `DiscoveryException` propagates; all other exceptions caught and wrapped as error `DetectorResult`
- `backend/tests/test_analysis/test_pipeline.py` — 27 tests across 7 test classes covering construction, execution order, failure handling, warning preservation, timestamps, determinism, and boundary enforcement

### Changed
- `backend/app/modules/analysis/types.py` — Added `DetectorWarning(detector_name, message)` frozen dataclass; added `warnings: tuple[DetectorWarning, ...]` field to `DetectorResult` (default `()`, zero breakage)
- `docs/ARCHITECTURE.md` — Added AnalysisPipeline orchestration section, updated folder structure and milestone map
- `docs/Legacy2Next_PROJECT_STATE.md` — Updated milestone progress, session log, current state

### Architecture
- Pipeline is a pure coordinator — no detection, no aggregation, no persistence
- Structured `DetectorWarning` (not raw strings) enables grouping by detector and future severity support
- Warnings preserved per-detector — pipeline never merges or rewrites them
- All 285 tests passing in test_analysis

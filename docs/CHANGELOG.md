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

from collections import Counter

from app.modules.analysis.metric_keys import MetricKey
from app.modules.analysis.types import AnalysisResults, DetectedMetric, DetectorResult


_MANIFEST_FILENAMES: frozenset[str] = frozenset({
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "pom.xml",
    "build.gradle",
    "cargo.toml",
    "composer.json",
    "gemfile",
})

_MANIFEST_EXTENSIONS: frozenset[str] = frozenset({
    ".csproj",
})


class MetricsCollector:
    detector_name: str = "MetricsCollector"

    def collect(self, results: AnalysisResults) -> DetectorResult:
        metrics: list[DetectedMetric] = []

        metrics.append(self._total_files(results))
        metrics.append(self._total_file_size(results))

        primary = self._primary_language(results)
        if primary is not None:
            metrics.append(self._language_count(results))
            metrics.append(primary)
        else:
            metrics.append(self._language_count(results))

        metrics.append(self._framework_count(results))
        metrics.append(self._dependency_count(results))
        metrics.extend(self._ecosystem_metrics(results))
        metrics.append(self._manifest_count(results))

        return DetectorResult(
            detector_name=self.detector_name,
            metrics=tuple(metrics),
        )

    def _total_files(self, results: AnalysisResults) -> DetectedMetric:
        return DetectedMetric(key=MetricKey.PROJECT_TOTAL_FILES, value=len(results.all_files))

    def _total_file_size(self, results: AnalysisResults) -> DetectedMetric:
        return DetectedMetric(
            key=MetricKey.PROJECT_TOTAL_FILE_SIZE,
            value=sum(f.file_size for f in results.all_files),
        )

    def _language_count(self, results: AnalysisResults) -> DetectedMetric:
        languages = {f.language for f in results.all_files if f.language}
        return DetectedMetric(key=MetricKey.LANGUAGE_COUNT, value=len(languages))

    def _primary_language(self, results: AnalysisResults) -> DetectedMetric | None:
        languages = [f.language for f in results.all_files if f.language]
        if not languages:
            return None
        counts = Counter(languages)
        max_count = max(counts.values())
        candidates = sorted(lang for lang, count in counts.items() if count == max_count)
        return DetectedMetric(key=MetricKey.PRIMARY_LANGUAGE, value=candidates[0])

    def _framework_count(self, results: AnalysisResults) -> DetectedMetric:
        count = sum(1 for t in results.all_technologies if t.category == "framework")
        return DetectedMetric(key=MetricKey.FRAMEWORK_COUNT, value=count)

    def _dependency_count(self, results: AnalysisResults) -> DetectedMetric:
        return DetectedMetric(key=MetricKey.DEPENDENCY_COUNT, value=len(results.all_dependencies))

    def _ecosystem_metrics(self, results: AnalysisResults) -> list[DetectedMetric]:
        ecosystems: dict[str, int] = {}
        for dep in results.all_dependencies:
            eco = dep.ecosystem or "unknown"
            ecosystems[eco] = ecosystems.get(eco, 0) + 1
        return [
            DetectedMetric(key=f"dependencies.{eco}", value=count)
            for eco, count in sorted(ecosystems.items())
        ]

    def _manifest_count(self, results: AnalysisResults) -> DetectedMetric:
        count = 0
        for f in results.all_files:
            if f.file_name.lower() in _MANIFEST_FILENAMES:
                count += 1
            elif f.extension.lower() in _MANIFEST_EXTENSIONS:
                count += 1
        return DetectedMetric(key=MetricKey.MANIFEST_COUNT, value=count)

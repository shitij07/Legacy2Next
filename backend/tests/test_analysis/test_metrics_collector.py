import copy

import pytest

from app.modules.analysis.metric_keys import MetricKey
from app.modules.analysis.metrics_collector import MetricsCollector
from app.modules.analysis.types import (
    AnalysisResults,
    DetectedDependency,
    DetectedFile,
    DetectedMetric,
    DetectedTechnology,
    DetectorResult,
)


@pytest.fixture
def collector() -> MetricsCollector:
    return MetricsCollector()


@pytest.fixture
def empty_results() -> AnalysisResults:
    return AnalysisResults(results=[], start_time=0.0)


def _make_results(
    files: list[DetectedFile] | None = None,
    technologies: list[DetectedTechnology] | None = None,
    dependencies: list[DetectedDependency] | None = None,
) -> AnalysisResults:
    return AnalysisResults(
        results=[
            DetectorResult(
                detector_name="Test",
                files=tuple(files or []),
                technologies=tuple(technologies or []),
                dependencies=tuple(dependencies or []),
            )
        ],
        start_time=0.0,
    )


# ─── Empty results ───────────────────────────────────────────────────


class TestEmptyResults:
    def test_empty_returns_detector_result(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        assert isinstance(result, DetectorResult)

    def test_empty_has_metrics_only(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        assert result.detector_name == "MetricsCollector"
        assert result.technologies == ()
        assert result.files == ()
        assert result.dependencies == ()
        assert result.error is None

    def test_empty_metric_keys(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        keys = [m.key for m in result.metrics]
        assert MetricKey.PROJECT_TOTAL_FILES in keys
        assert MetricKey.PROJECT_TOTAL_FILE_SIZE in keys
        assert MetricKey.LANGUAGE_COUNT in keys
        assert MetricKey.FRAMEWORK_COUNT in keys
        assert MetricKey.DEPENDENCY_COUNT in keys
        assert MetricKey.MANIFEST_COUNT in keys

    def test_empty_no_primary_language(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        keys = [m.key for m in result.metrics]
        assert MetricKey.PRIMARY_LANGUAGE not in keys

    def test_empty_zero_values(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        metrics_map = {m.key: m.value for m in result.metrics}
        assert metrics_map[MetricKey.PROJECT_TOTAL_FILES] == 0
        assert metrics_map[MetricKey.PROJECT_TOTAL_FILE_SIZE] == 0
        assert metrics_map[MetricKey.LANGUAGE_COUNT] == 0
        assert metrics_map[MetricKey.FRAMEWORK_COUNT] == 0
        assert metrics_map[MetricKey.DEPENDENCY_COUNT] == 0
        assert metrics_map[MetricKey.MANIFEST_COUNT] == 0


# ─── Total files ─────────────────────────────────────────────────────


class TestTotalFiles:
    def test_single_file(self, collector: MetricsCollector):
        results = _make_results(files=[DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=100)])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PROJECT_TOTAL_FILES)
        assert metric.value == 1

    def test_multiple_files(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="a.py", file_name="a.py", extension=".py", file_size=10),
            DetectedFile(relative_path="b.py", file_name="b.py", extension=".py", file_size=20),
            DetectedFile(relative_path="c.py", file_name="c.py", extension=".py", file_size=30),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PROJECT_TOTAL_FILES)
        assert metric.value == 3

    def test_zero_files(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PROJECT_TOTAL_FILES)
        assert metric.value == 0


# ─── Total file size ─────────────────────────────────────────────────


class TestTotalFileSize:
    def test_single_file(self, collector: MetricsCollector):
        results = _make_results(files=[DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=1024)])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PROJECT_TOTAL_FILE_SIZE)
        assert metric.value == 1024

    def test_multiple_files(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="a.py", file_name="a.py", extension=".py", file_size=100),
            DetectedFile(relative_path="b.py", file_name="b.py", extension=".py", file_size=200),
            DetectedFile(relative_path="c.py", file_name="c.py", extension=".py", file_size=300),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PROJECT_TOTAL_FILE_SIZE)
        assert metric.value == 600

    def test_zero_file_size(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PROJECT_TOTAL_FILE_SIZE)
        assert metric.value == 0

    def test_empty_files_have_no_size(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="empty.py", file_name="empty.py", extension=".py", file_size=0),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PROJECT_TOTAL_FILE_SIZE)
        assert metric.value == 0


# ─── Language counting ───────────────────────────────────────────────


class TestLanguageCount:
    def test_single_language(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=10, language="Python"),
            DetectedFile(relative_path="utils.py", file_name="utils.py", extension=".py", file_size=20, language="Python"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.LANGUAGE_COUNT)
        assert metric.value == 1

    def test_multiple_languages(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=10, language="Python"),
            DetectedFile(relative_path="app.js", file_name="app.js", extension=".js", file_size=20, language="JavaScript"),
            DetectedFile(relative_path="style.css", file_name="style.css", extension=".css", file_size=30, language="CSS"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.LANGUAGE_COUNT)
        assert metric.value == 3

    def test_unknown_language_not_counted(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=10, language="Python"),
            DetectedFile(relative_path="binary.bin", file_name="binary.bin", extension=".bin", file_size=100, language=None),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.LANGUAGE_COUNT)
        assert metric.value == 1

    def test_all_unknown_languages(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="a.bin", file_name="a.bin", extension=".bin", file_size=10, language=None),
            DetectedFile(relative_path="b.bin", file_name="b.bin", extension=".bin", file_size=20, language=None),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.LANGUAGE_COUNT)
        assert metric.value == 0


# ─── Primary language ────────────────────────────────────────────────


class TestPrimaryLanguage:
    def test_single_language(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=10, language="Python"),
            DetectedFile(relative_path="utils.py", file_name="utils.py", extension=".py", file_size=20, language="Python"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PRIMARY_LANGUAGE)
        assert metric.value == "Python"

    def test_most_common_language(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="a.py", file_name="a.py", extension=".py", file_size=10, language="Python"),
            DetectedFile(relative_path="b.js", file_name="b.js", extension=".js", file_size=20, language="JavaScript"),
            DetectedFile(relative_path="c.js", file_name="c.js", extension=".js", file_size=30, language="JavaScript"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PRIMARY_LANGUAGE)
        assert metric.value == "JavaScript"

    def test_alphabetical_tie_breaking(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="a.py", file_name="a.py", extension=".py", file_size=10, language="Python"),
            DetectedFile(relative_path="b.js", file_name="b.js", extension=".js", file_size=20, language="JavaScript"),
            DetectedFile(relative_path="c.rb", file_name="c.rb", extension=".rb", file_size=30, language="Ruby"),
            DetectedFile(relative_path="d.java", file_name="d.java", extension=".java", file_size=40, language="Java"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PRIMARY_LANGUAGE)
        assert metric.value == "Java"

    def test_alphabetical_tie_two_way(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="a.ts", file_name="a.ts", extension=".ts", file_size=10, language="TypeScript"),
            DetectedFile(relative_path="b.ts", file_name="b.ts", extension=".ts", file_size=20, language="TypeScript"),
            DetectedFile(relative_path="c.py", file_name="c.py", extension=".py", file_size=30, language="Python"),
            DetectedFile(relative_path="d.py", file_name="d.py", extension=".py", file_size=40, language="Python"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.PRIMARY_LANGUAGE)
        assert metric.value == "Python"

    def test_no_language_omits_metric(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        keys = [m.key for m in result.metrics]
        assert MetricKey.PRIMARY_LANGUAGE not in keys

    def test_no_language_with_files_omits_metric(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="a.bin", file_name="a.bin", extension=".bin", file_size=10, language=None),
        ])
        result = collector.collect(results)
        keys = [m.key for m in result.metrics]
        assert MetricKey.PRIMARY_LANGUAGE not in keys


# ─── Framework count ─────────────────────────────────────────────────


class TestFrameworkCount:
    def test_no_frameworks(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        metric = next(m for m in result.metrics if m.key == MetricKey.FRAMEWORK_COUNT)
        assert metric.value == 0

    def test_single_framework(self, collector: MetricsCollector):
        results = _make_results(technologies=[
            DetectedTechnology(name="Django", category="framework"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.FRAMEWORK_COUNT)
        assert metric.value == 1

    def test_multiple_frameworks(self, collector: MetricsCollector):
        results = _make_results(technologies=[
            DetectedTechnology(name="Django", category="framework"),
            DetectedTechnology(name="React", category="framework"),
            DetectedTechnology(name="PostgreSQL", category="database"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.FRAMEWORK_COUNT)
        assert metric.value == 2

    def test_non_framework_not_counted(self, collector: MetricsCollector):
        results = _make_results(technologies=[
            DetectedTechnology(name="Python", category="language"),
            DetectedTechnology(name="npm", category="package-manager"),
            DetectedTechnology(name="Docker", category="tool"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.FRAMEWORK_COUNT)
        assert metric.value == 0


# ─── Dependency count ────────────────────────────────────────────────


class TestDependencyCount:
    def test_no_dependencies(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        metric = next(m for m in result.metrics if m.key == MetricKey.DEPENDENCY_COUNT)
        assert metric.value == 0

    def test_single_dependency(self, collector: MetricsCollector):
        results = _make_results(dependencies=[
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.DEPENDENCY_COUNT)
        assert metric.value == 1

    def test_multiple_dependencies(self, collector: MetricsCollector):
        results = _make_results(dependencies=[
            DetectedDependency(name="react", version="18.0.0", ecosystem="npm"),
            DetectedDependency(name="express", version="4.18.0", ecosystem="npm"),
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip"),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.DEPENDENCY_COUNT)
        assert metric.value == 3


# ─── Ecosystem metrics ───────────────────────────────────────────────


class TestEcosystemMetrics:
    def test_single_ecosystem(self, collector: MetricsCollector):
        results = _make_results(dependencies=[
            DetectedDependency(name="react", version="18.0.0", ecosystem="npm"),
            DetectedDependency(name="express", version="4.18.0", ecosystem="npm"),
        ])
        result = collector.collect(results)
        metrics_map = {m.key: m.value for m in result.metrics}
        assert metrics_map.get("dependencies.npm") == 2

    def test_multiple_ecosystems(self, collector: MetricsCollector):
        results = _make_results(dependencies=[
            DetectedDependency(name="react", version="18.0.0", ecosystem="npm"),
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip"),
            DetectedDependency(name="django", version="5.0.0", ecosystem="pip"),
        ])
        result = collector.collect(results)
        metrics_map = {m.key: m.value for m in result.metrics}
        assert metrics_map.get("dependencies.npm") == 1
        assert metrics_map.get("dependencies.pip") == 2

    def test_ecosystem_alphabetical_order(self, collector: MetricsCollector):
        results = _make_results(dependencies=[
            DetectedDependency(name="react", version="18.0.0", ecosystem="npm"),
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip"),
            DetectedDependency(name="cargo-pkg", version="1.0.0", ecosystem="cargo"),
        ])
        result = collector.collect(results)
        dep_metrics = [m for m in result.metrics if m.key.count(".") > 1]
        keys = [str(m.key) for m in dep_metrics]
        assert keys == sorted(keys)

    def test_no_dependencies_no_ecosystem_metrics(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        dep_metrics = [m for m in result.metrics if m.key.count(".") > 1]
        assert len(dep_metrics) == 0

    def test_missing_ecosystem_falls_back_to_unknown(self, collector: MetricsCollector):
        results = _make_results(dependencies=[
            DetectedDependency(name="something", version="1.0.0", ecosystem=None),
            DetectedDependency(name="other", version="2.0.0", ecosystem=None),
        ])
        result = collector.collect(results)
        metrics_map = {m.key: m.value for m in result.metrics}
        assert metrics_map.get("dependencies.unknown") == 2


# ─── Manifest count ──────────────────────────────────────────────────


class TestManifestCount:
    def test_no_manifests(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        metric = next(m for m in result.metrics if m.key == MetricKey.MANIFEST_COUNT)
        assert metric.value == 0

    def test_package_json_manifest(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="package.json", file_name="package.json", extension=".json", file_size=50),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.MANIFEST_COUNT)
        assert metric.value == 1

    def test_csproj_manifest(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="src/MyApp.csproj", file_name="MyApp.csproj", extension=".csproj", file_size=200),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.MANIFEST_COUNT)
        assert metric.value == 1

    def test_multiple_manifests(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="package.json", file_name="package.json", extension=".json", file_size=50),
            DetectedFile(relative_path="requirements.txt", file_name="requirements.txt", extension=".txt", file_size=30),
            DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=100),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.MANIFEST_COUNT)
        assert metric.value == 2

    def test_gemfile_manifest(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="Gemfile", file_name="Gemfile", extension="", file_size=40),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.MANIFEST_COUNT)
        assert metric.value == 1

    def test_regular_file_not_counted(self, collector: MetricsCollector):
        results = _make_results(files=[
            DetectedFile(relative_path="src/main.py", file_name="main.py", extension=".py", file_size=100),
            DetectedFile(relative_path="src/utils.js", file_name="utils.js", extension=".js", file_size=200),
        ])
        result = collector.collect(results)
        metric = next(m for m in result.metrics if m.key == MetricKey.MANIFEST_COUNT)
        assert metric.value == 0


# ─── Determinism ─────────────────────────────────────────────────────


class TestDeterminism:
    def test_deterministic_ordering(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result1 = collector.collect(empty_results)
        result2 = collector.collect(empty_results)
        keys1 = [m.key for m in result1.metrics]
        keys2 = [m.key for m in result2.metrics]
        assert keys1 == keys2

    def test_deterministic_values(self, collector: MetricsCollector):
        files = [
            DetectedFile(relative_path="a.py", file_name="a.py", extension=".py", file_size=10, language="Python"),
            DetectedFile(relative_path="b.js", file_name="b.js", extension=".js", file_size=20, language="JavaScript"),
        ]
        techs = [
            DetectedTechnology(name="Django", category="framework"),
        ]
        deps = [
            DetectedDependency(name="react", version="18.0.0", ecosystem="npm"),
        ]
        results = _make_results(files=files, technologies=techs, dependencies=deps)
        result1 = collector.collect(results)
        result2 = collector.collect(results)
        assert result1.metrics == result2.metrics

    def test_repeated_execution_stable(self, collector: MetricsCollector):
        files = [
            DetectedFile(relative_path="a.py", file_name="a.py", extension=".py", file_size=10, language="Python"),
            DetectedFile(relative_path="b.js", file_name="b.js", extension=".js", file_size=20, language="JavaScript"),
            DetectedFile(relative_path="c.js", file_name="c.js", extension=".js", file_size=30, language="JavaScript"),
        ]
        results = _make_results(files=files)
        for _ in range(5):
            result = collector.collect(results)
            primary = next(m for m in result.metrics if m.key == MetricKey.PRIMARY_LANGUAGE)
            assert primary.value == "JavaScript"


# ─── Result integrity ────────────────────────────────────────────────


class TestResultIntegrity:
    def test_metrics_only_in_result(self, collector: MetricsCollector):
        results = _make_results(
            files=[DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=100, language="Python")],
            technologies=[DetectedTechnology(name="Django", category="framework")],
            dependencies=[DetectedDependency(name="requests", version="2.31.0", ecosystem="pip")],
        )
        result = collector.collect(results)
        assert result.files == ()
        assert result.technologies == ()
        assert result.dependencies == ()
        assert len(result.metrics) > 0

    def test_detector_name(self, collector: MetricsCollector):
        results = _make_results()
        result = collector.collect(results)
        assert result.detector_name == "MetricsCollector"

    def test_analysis_results_unchanged(self, collector: MetricsCollector):
        files = [DetectedFile(relative_path="main.py", file_name="main.py", extension=".py", file_size=100, language="Python")]
        original_results = _make_results(files=files)
        results_copy = copy.deepcopy(original_results)
        collector.collect(original_results)
        assert original_results.start_time == results_copy.start_time
        assert original_results.end_time == results_copy.end_time
        assert len(original_results.results) == len(results_copy.results)
        assert original_results.all_files == results_copy.all_files


# ─── Integration ─────────────────────────────────────────────────────


class TestIntegration:
    def test_full_project(self, collector: MetricsCollector):
        files = [
            DetectedFile(relative_path="src/main.py", file_name="main.py", extension=".py", file_size=200, language="Python"),
            DetectedFile(relative_path="src/utils.py", file_name="utils.py", extension=".py", file_size=150, language="Python"),
            DetectedFile(relative_path="src/app.js", file_name="app.js", extension=".js", file_size=300, language="JavaScript"),
            DetectedFile(relative_path="package.json", file_name="package.json", extension=".json", file_size=80),
            DetectedFile(relative_path="requirements.txt", file_name="requirements.txt", extension=".txt", file_size=40),
        ]
        technologies = [
            DetectedTechnology(name="Django", category="framework"),
            DetectedTechnology(name="React", category="framework"),
            DetectedTechnology(name="Python", category="language"),
        ]
        dependencies = [
            DetectedDependency(name="react", version="18.0.0", ecosystem="npm"),
            DetectedDependency(name="express", version="4.18.0", ecosystem="npm"),
            DetectedDependency(name="django", version="5.0.0", ecosystem="pip"),
            DetectedDependency(name="requests", version="2.31.0", ecosystem="pip"),
        ]
        results = _make_results(files=files, technologies=technologies, dependencies=dependencies)
        result = collector.collect(results)
        metrics = {m.key: m.value for m in result.metrics}

        assert metrics[MetricKey.PROJECT_TOTAL_FILES] == 5
        assert metrics[MetricKey.PROJECT_TOTAL_FILE_SIZE] == 770
        assert metrics[MetricKey.LANGUAGE_COUNT] == 2
        assert metrics[MetricKey.PRIMARY_LANGUAGE] == "Python"
        assert metrics[MetricKey.FRAMEWORK_COUNT] == 2
        assert metrics[MetricKey.DEPENDENCY_COUNT] == 4
        assert metrics[MetricKey.MANIFEST_COUNT] == 2
        assert metrics["dependencies.npm"] == 2
        assert metrics["dependencies.pip"] == 2

    def test_missing_all_data(self, collector: MetricsCollector, empty_results: AnalysisResults):
        result = collector.collect(empty_results)
        metrics = {m.key: m.value for m in result.metrics}
        assert metrics[MetricKey.PROJECT_TOTAL_FILES] == 0
        assert metrics[MetricKey.PROJECT_TOTAL_FILE_SIZE] == 0
        assert metrics[MetricKey.LANGUAGE_COUNT] == 0
        assert MetricKey.PRIMARY_LANGUAGE not in metrics
        assert metrics[MetricKey.FRAMEWORK_COUNT] == 0
        assert metrics[MetricKey.DEPENDENCY_COUNT] == 0
        assert metrics[MetricKey.MANIFEST_COUNT] == 0

    def test_multiple_detector_results_aggregated(self, collector: MetricsCollector):
        results = AnalysisResults(
            results=[
                DetectorResult(
                    detector_name="DetectorA",
                    files=(
                        DetectedFile(relative_path="a.py", file_name="a.py", extension=".py", file_size=100, language="Python"),
                    ),
                    technologies=(),
                    dependencies=(),
                ),
                DetectorResult(
                    detector_name="DetectorB",
                    files=(
                        DetectedFile(relative_path="b.js", file_name="b.js", extension=".js", file_size=200, language="JavaScript"),
                    ),
                    technologies=(
                        DetectedTechnology(name="React", category="framework"),
                    ),
                    dependencies=(
                        DetectedDependency(name="react", version="18.0.0", ecosystem="npm"),
                    ),
                ),
            ],
            start_time=0.0,
        )
        result = collector.collect(results)
        metrics = {m.key: m.value for m in result.metrics}
        assert metrics[MetricKey.PROJECT_TOTAL_FILES] == 2
        assert metrics[MetricKey.LANGUAGE_COUNT] == 2
        assert metrics[MetricKey.FRAMEWORK_COUNT] == 1
        assert metrics[MetricKey.DEPENDENCY_COUNT] == 1


# ─── MetricKey enum ──────────────────────────────────────────────────


class TestMetricKeyEnum:
    def test_enum_values(self):
        assert MetricKey.PROJECT_TOTAL_FILES == "project.total_files"
        assert MetricKey.PROJECT_TOTAL_FILE_SIZE == "project.total_file_size"
        assert MetricKey.LANGUAGE_COUNT == "languages.count"
        assert MetricKey.PRIMARY_LANGUAGE == "languages.primary"
        assert MetricKey.FRAMEWORK_COUNT == "frameworks.count"
        assert MetricKey.DEPENDENCY_COUNT == "dependencies.count"
        assert MetricKey.MANIFEST_COUNT == "manifests.count"

    def test_enum_is_str(self):
        assert isinstance(MetricKey.PROJECT_TOTAL_FILES, str)
        assert MetricKey.PROJECT_TOTAL_FILES.upper() == "PROJECT.TOTAL_FILES"

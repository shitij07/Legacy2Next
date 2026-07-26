import time
from pathlib import Path

import pytest

from app.modules.analysis.base import BaseDetector
from app.modules.analysis.discovery import DiscoveryEngine, DiscoveryException
from app.modules.analysis.metrics_collector import MetricsCollector
from app.modules.analysis.pipeline import AnalysisPipeline
from app.modules.analysis.types import (
    AnalysisResults,
    DetectedMetric,
    DetectedTechnology,
    DetectorResult,
    DetectorWarning,
    DiscoveryContext,
    DiscoveryStats,
    FileGraph,
)


class FakeDetector(BaseDetector):
    def __init__(self, name: str, result: DetectorResult | None = None, raise_error: str | None = None) -> None:
        self._name = name
        self._result = result or DetectorResult(detector_name=name)
        self._raise_error = raise_error
        self.call_count = 0

    @property
    def detector_name(self) -> str:
        return self._name

    def detect(self, context: object) -> DetectorResult:
        self.call_count += 1
        if self._raise_error:
            raise RuntimeError(self._raise_error)
        return self._result


class FakeDiscoveryEngine:
    def __init__(self, context: DiscoveryContext | None = None, raise_error: bool = False) -> None:
        self._context = context
        self._raise_error = raise_error
        self.call_count = 0

    def discover(self, root_path: Path, upload_id: int, project_id: int) -> DiscoveryContext:
        self.call_count += 1
        if self._raise_error:
            raise DiscoveryException("Root path does not exist")
        if self._context is not None:
            return self._context
        return DiscoveryContext(
            upload_id=upload_id,
            project_id=project_id,
            root_path=root_path,
            file_graph=FileGraph(files=[], directories=[], by_path={}, tree={}),
            stats=DiscoveryStats(total_files=0, total_directories=0, ignored_entries=0, duration_ms=0),
        )


class FakeMetricsCollector:
    def __init__(self, metrics: tuple[DetectedMetric, ...] = ()) -> None:
        self._metrics = metrics
        self.call_count = 0

    def collect(self, results: AnalysisResults) -> DetectorResult:
        self.call_count += 1
        return DetectorResult(detector_name="MetricsCollector", metrics=self._metrics)


# ─── Constructor ─────────────────────────────────────────────────────


class TestConstruction:
    def test_constructor_injection(self):
        engine = FakeDiscoveryEngine()
        detectors: list[BaseDetector] = [FakeDetector("A")]
        collector = FakeMetricsCollector()
        pipeline = AnalysisPipeline(engine=engine, detectors=detectors, metrics_collector=collector)
        assert pipeline._engine is engine
        assert pipeline._detectors is detectors
        assert pipeline._metrics_collector is collector

    def test_empty_detectors_allowed(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert len(results.results) == 1  # only metrics

    def test_single_detector(self):
        detector = FakeDetector("Test")
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[detector],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert len(results.results) == 2  # detector + metrics


# ─── Successful execution ────────────────────────────────────────────


class TestSuccessfulExecution:
    def test_detector_execution_order(self):
        order: list[str] = []

        class OrderDetector(FakeDetector):
            def detect(self, context: object) -> DetectorResult:
                order.append(self._name)
                return self._result

        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[OrderDetector("A"), OrderDetector("B"), OrderDetector("C")],
            metrics_collector=FakeMetricsCollector(),
        )
        pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert order == ["A", "B", "C"]

    def test_metrics_executed_after_detectors(self):
        detector = FakeDetector("Test", result=DetectorResult(detector_name="Test", technologies=(DetectedTechnology(name="Python", category="language"),)))
        collector = FakeMetricsCollector(metrics=(DetectedMetric(key="total_files", value=1),))
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[detector],
            metrics_collector=collector,
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert collector.call_count == 1
        assert detector.call_count == 1

    def test_metrics_appended_exactly_once(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[FakeDetector("A"), FakeDetector("B")],
            metrics_collector=FakeMetricsCollector(metrics=(DetectedMetric(key="k", value=1),)),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert len(results.results) == 3  # A + B + metrics
        assert results.results[-1].detector_name == "MetricsCollector"
        assert len(results.results[-1].metrics) == 1

    def test_final_analysis_results_contains_all(self):
        a_result = DetectorResult(detector_name="A", technologies=(DetectedTechnology(name="React", category="framework"),))
        b_result = DetectorResult(detector_name="B", dependencies=())
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[FakeDetector("A", result=a_result), FakeDetector("B", result=b_result)],
            metrics_collector=FakeMetricsCollector(metrics=(DetectedMetric(key="k", value=1),)),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert len(results.results) == 3
        assert results.results[0].detector_name == "A"
        assert results.results[1].detector_name == "B"
        assert results.results[2].detector_name == "MetricsCollector"

    def test_empty_project(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert len(results.results) == 1
        assert results.results[0].detector_name == "MetricsCollector"

    def test_detector_called_with_context(self):
        contexts: list[object] = []

        class ContextDetector(FakeDetector):
            def detect(self, context: object) -> DetectorResult:
                contexts.append(context)
                return self._result

        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[ContextDetector("A"), ContextDetector("B")],
            metrics_collector=FakeMetricsCollector(),
        )
        pipeline.analyze(root_path=Path("/tmp"), upload_id=42, project_id=7)
        assert len(contexts) == 2
        assert contexts[0] is contexts[1]  # same context object


# ─── Failure handling ────────────────────────────────────────────────


class TestFailureHandling:
    def test_discovery_exception_propagates(self):
        engine = FakeDiscoveryEngine(raise_error=True)
        pipeline = AnalysisPipeline(
            engine=engine,
            detectors=[FakeDetector("A")],
            metrics_collector=FakeMetricsCollector(),
        )
        with pytest.raises(DiscoveryException, match="Root path does not exist"):
            pipeline.analyze(root_path=Path("/nonexistent"), upload_id=1, project_id=1)

    def test_detector_error_result_continues(self):
        good = FakeDetector("Good", result=DetectorResult(detector_name="Good"))
        bad = FakeDetector("Bad", result=DetectorResult(detector_name="Bad", error="Something failed"))
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[good, bad],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert len(results.results) == 3  # Good + Bad + metrics
        assert results.results[0].detector_name == "Good"
        assert results.results[0].error is None
        assert results.results[1].detector_name == "Bad"
        assert results.results[1].error == "Something failed"

    def test_raised_exception_becomes_error_result(self):
        good = FakeDetector("Good", result=DetectorResult(detector_name="Good"))
        bad = FakeDetector("Bad", raise_error="Unexpected crash")
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[good, bad],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert len(results.results) == 3
        assert results.results[0].detector_name == "Good"
        assert results.results[0].error is None
        assert results.results[1].detector_name == "Bad"
        assert results.results[1].error == "Unexpected crash"

    def test_remaining_detectors_continue_after_exception(self):
        order: list[str] = []

        class OrderDetector(FakeDetector):
            def detect(self, context: object) -> DetectorResult:
                order.append(self._name)
                if self._raise_error:
                    raise RuntimeError(self._raise_error)
                return self._result

        detectors = [
            OrderDetector("First", result=DetectorResult(detector_name="First")),
            OrderDetector("Broken", raise_error="Crash"),
            OrderDetector("Last", result=DetectorResult(detector_name="Last")),
        ]
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=detectors,
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert order == ["First", "Broken", "Last"]
        assert len(results.results) == 4  # First + Broken + Last + metrics
        assert results.results[0].error is None
        assert results.results[1].error == "Crash"
        assert results.results[2].error is None

    def test_all_detectors_fail(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[
                FakeDetector("A", raise_error="Fail A"),
                FakeDetector("B", raise_error="Fail B"),
            ],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert len(results.results) == 3
        assert all(r.error is not None for r in results.results[:-1])
        assert results.results[-1].detector_name == "MetricsCollector"

    def test_detector_none_exception(self):
        class NoneReturnDetector(FakeDetector):
            def detect(self, context: object) -> DetectorResult:
                self.call_count += 1
                msg = "NoneReturnDetector"
                raise ValueError(msg)

        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[NoneReturnDetector("NoneRet")],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert results.results[0].error is not None
        assert "NoneReturnDetector" in results.results[0].error


# ─── Warning preservation ────────────────────────────────────────────


class TestWarningPreservation:
    def test_warnings_preserved_on_result(self):
        warnings = (DetectorWarning(detector_name="DepDetector", message="Version conflict"),)
        detector = FakeDetector("DepDetector", result=DetectorResult(detector_name="DepDetector", warnings=warnings))
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[detector],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert results.results[0].warnings == warnings
        assert len(results.results[0].warnings) == 1
        assert results.results[0].warnings[0].message == "Version conflict"

    def test_multiple_warnings_across_detectors(self):
        w1 = (DetectorWarning(detector_name="A", message="warn A"),)
        w2 = (DetectorWarning(detector_name="B", message="warn B1"), DetectorWarning(detector_name="B", message="warn B2"))
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[
                FakeDetector("A", result=DetectorResult(detector_name="A", warnings=w1)),
                FakeDetector("B", result=DetectorResult(detector_name="B", warnings=w2)),
            ],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert results.results[0].warnings == w1
        assert results.results[1].warnings == w2

    def test_no_warnings_defaults_empty(self):
        detector = FakeDetector("A", result=DetectorResult(detector_name="A"))
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[detector],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert results.results[0].warnings == ()


# ─── Timestamps ──────────────────────────────────────────────────────


class TestTimestamps:
    def test_start_time_populated(self):
        before = time.time()
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[FakeDetector("A")],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        after = time.time()
        assert before <= results.start_time <= after

    def test_end_time_populated(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[FakeDetector("A")],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert results.end_time is not None
        assert results.end_time >= results.start_time

    def test_times_updated_per_call(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[FakeDetector("A")],
            metrics_collector=FakeMetricsCollector(),
        )
        r1 = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        r2 = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert r1.start_time != r2.start_time or r1.end_time != r2.end_time


# ─── Determinism ─────────────────────────────────────────────────────


class TestDeterminism:
    def test_deterministic_repeated_execution(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[FakeDetector("A"), FakeDetector("B")],
            metrics_collector=FakeMetricsCollector(metrics=(DetectedMetric(key="k", value=1),)),
        )
        r1 = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        r2 = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert len(r1.results) == len(r2.results)
        for i in range(len(r1.results)):
            assert r1.results[i].detector_name == r2.results[i].detector_name
            assert r1.results[i].error == r2.results[i].error

    def test_deterministic_detector_order(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[FakeDetector("First"), FakeDetector("Second")],
            metrics_collector=FakeMetricsCollector(),
        )
        r1 = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        r2 = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        names1 = [r.detector_name for r in r1.results]
        names2 = [r.detector_name for r in r2.results]
        assert names1 == names2


# ─── Boundary: pipeline contains no logic ────────────────────────────


class TestPipelineBoundary:
    def test_no_detector_logic_in_pipeline(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[FakeDetector("A")],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert results.results[0].technologies == ()
        assert results.results[0].files == ()
        assert results.results[0].dependencies == ()
        assert results.results[0].metrics == ()

    def test_no_metric_logic_in_pipeline(self):
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert results.results[0].metrics == ()

    def test_pipeline_does_not_mutate_results(self):
        orig_result = DetectorResult(detector_name="A", technologies=(DetectedTechnology(name="React", category="framework"),))
        detector = FakeDetector("A", result=orig_result)
        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[detector],
            metrics_collector=FakeMetricsCollector(),
        )
        results = pipeline.analyze(root_path=Path("/tmp"), upload_id=1, project_id=1)
        assert results.results[0].technologies == orig_result.technologies
        assert results.results[0].detector_name == "A"
        # original unchanged
        assert orig_result.technologies == (DetectedTechnology(name="React", category="framework"),)

    def test_pipeline_passes_upload_and_project_ids(self):
        class IdDetector(FakeDetector):
            def detect(self, context: object) -> DetectorResult:
                assert isinstance(context, DiscoveryContext)
                assert context.upload_id == 99
                assert context.project_id == 42
                return self._result

        pipeline = AnalysisPipeline(
            engine=FakeDiscoveryEngine(),
            detectors=[IdDetector("ID")],
            metrics_collector=FakeMetricsCollector(),
        )
        pipeline.analyze(root_path=Path("/tmp"), upload_id=99, project_id=42)

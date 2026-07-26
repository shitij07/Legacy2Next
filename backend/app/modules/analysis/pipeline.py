import time
from pathlib import Path

from app.modules.analysis.base import BaseDetector
from app.modules.analysis.discovery import DiscoveryEngine
from app.modules.analysis.metrics_collector import MetricsCollector
from app.modules.analysis.types import AnalysisResults, DetectorResult


class AnalysisPipeline:

    def __init__(
        self,
        engine: DiscoveryEngine,
        detectors: list[BaseDetector],
        metrics_collector: MetricsCollector,
    ) -> None:
        self._engine = engine
        self._detectors = detectors
        self._metrics_collector = metrics_collector

    def analyze(
        self,
        root_path: Path,
        upload_id: int,
        project_id: int,
    ) -> AnalysisResults:
        start_time = time.time()

        context = self._engine.discover(
            root_path=root_path,
            upload_id=upload_id,
            project_id=project_id,
        )

        results: list[DetectorResult] = self._run_detectors(context)
        intermediate = AnalysisResults(results=list(results), start_time=start_time)
        metrics_result = self._metrics_collector.collect(intermediate)
        results.append(metrics_result)

        return AnalysisResults(results=results, start_time=start_time, end_time=time.time())

    def _run_detectors(self, context: object) -> list[DetectorResult]:
        results: list[DetectorResult] = []
        for detector in self._detectors:
            try:
                result = detector.detect(context)
            except Exception as exc:
                result = DetectorResult(
                    detector_name=detector.detector_name,
                    error=str(exc),
                )
            results.append(result)
        return results

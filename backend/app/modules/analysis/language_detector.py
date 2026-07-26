from app.modules.analysis.base import BaseDetector
from app.modules.analysis.types import (
    DetectedFile,
    DetectedTechnology,
    DetectorResult,
    DiscoveryContext,
)
from app.modules.analysis.utils import classify_extension


class LanguageDetector(BaseDetector):

    def detect(self, context: DiscoveryContext) -> DetectorResult:
        try:
            return self._detect(context)
        except Exception as exc:
            self._logger.exception("Language detection failed")
            return DetectorResult(
                detector_name=self.detector_name,
                error=f"{type(exc).__name__}: {exc}",
            )

    def _detect(self, context: DiscoveryContext) -> DetectorResult:
        file_graph = context.file_graph
        total = len(file_graph.files)
        if total == 0:
            return DetectorResult(detector_name=self.detector_name)

        lang_files: dict[str, list[DetectedFile]] = {}
        unknown_files: list[DetectedFile] = []

        for node in file_graph.files:
            lang = classify_extension(node.extension)
            df = DetectedFile(
                relative_path=node.relative_path,
                file_name=node.file_name,
                extension=node.extension,
                file_size=node.file_size,
                language=lang,
            )
            if lang is None:
                unknown_files.append(df)
            else:
                lang_files.setdefault(lang, []).append(df)

        technologies: list[DetectedTechnology] = []
        for lang, detected_files in sorted(lang_files.items()):
            count = len(detected_files)
            pct = round(count / total * 100)
            technologies.append(DetectedTechnology(
                name=lang,
                category="language",
                evidence=f"{count} files ({pct}%)",
            ))

        if unknown_files:
            technologies.append(DetectedTechnology(
                name="Unknown",
                category="language",
                evidence=f"{len(unknown_files)} files",
                confidence="low",
            ))

        all_files = [f for lst in lang_files.values() for f in lst] + unknown_files

        return DetectorResult(
            detector_name=self.detector_name,
            technologies=tuple(technologies),
            files=tuple(all_files),
        )

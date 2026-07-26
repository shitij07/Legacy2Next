import logging
from abc import ABC, abstractmethod
from pathlib import Path

from app.modules.analysis.types import DetectorResult, DiscoveryContext


class BaseDetector(ABC):

    @abstractmethod
    def detect(self, context: DiscoveryContext) -> DetectorResult:
        ...

    @property
    def detector_name(self) -> str:
        return type(self).__name__

    @property
    def _logger(self) -> logging.Logger:
        name = f"{__name__}.{self.detector_name}"
        return logging.getLogger(name)

    def read_text(self, relative_path: str) -> str | None:
        root = getattr(self, "_context_root", None)
        if root is None:
            return None
        full = root / relative_path
        try:
            return full.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError) as exc:
            self._logger.warning("Cannot read %s: %s", relative_path, exc)
            return None

import fnmatch
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IgnorePattern:
    pattern: str
    match_type: str = "exact"


_DEFAULT_IGNORED_DIRECTORIES = [
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    "target",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
]

_DEFAULT_IGNORED_FILES = [
    ".DS_Store",
    "Thumbs.db",
]

_DEFAULT_IGNORED_GLOB = [
    "*.pyc",
    "*.pyo",
]


class IgnoreRules:
    def __init__(self, patterns: list[IgnorePattern] | None = None):
        self._patterns = list(patterns) if patterns else []

    @classmethod
    def defaults(cls) -> "IgnoreRules":
        patterns = [
            *(IgnorePattern(d) for d in _DEFAULT_IGNORED_DIRECTORIES),
            *(IgnorePattern(f) for f in _DEFAULT_IGNORED_FILES),
            *(IgnorePattern(g, match_type="glob") for g in _DEFAULT_IGNORED_GLOB),
        ]
        return cls(patterns)

    def should_ignore(self, rel_path: str, is_dir: bool) -> bool:
        name = Path(rel_path).name
        for p in self._patterns:
            if p.match_type == "exact":
                if name == p.pattern:
                    return True
            elif p.match_type == "glob":
                if fnmatch.fnmatch(name, p.pattern):
                    return True
            elif p.match_type == "prefix":
                if rel_path.startswith(p.pattern):
                    return True
            elif p.match_type == "suffix":
                if rel_path.endswith(p.pattern):
                    return True
        return False

    @property
    def patterns(self) -> list[IgnorePattern]:
        return list(self._patterns)

import json
import re
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.modules.analysis.base import BaseDetector
from app.modules.analysis.types import (
    DetectedDependency,
    DetectorResult,
    DiscoveryContext,
)


@dataclass(frozen=True)
class _RawDependency:
    name: str
    version: str | None
    ecosystem: str
    category: str
    source_file: str


class ManifestParser(ABC):

    @abstractmethod
    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        ...


class PackageJsonParser(ManifestParser):

    _CATEGORY_MAP = {
        "dependencies": "runtime",
        "devDependencies": "development",
        "peerDependencies": "peer",
        "optionalDependencies": "optional",
    }

    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        warnings: list[str] = []
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            warnings.append(f"{source_file}: invalid JSON ({exc})")
            return [], warnings
        if not isinstance(data, dict):
            warnings.append(f"{source_file}: root value is not an object")
            return [], warnings

        results: list[_RawDependency] = []
        for section, category in self._CATEGORY_MAP.items():
            entries = data.get(section)
            if not isinstance(entries, dict):
                continue
            for name, specifier in entries.items():
                if isinstance(specifier, str):
                    version = specifier
                elif isinstance(specifier, dict):
                    version = specifier.get("version", None)
                else:
                    version = None
                results.append(_RawDependency(
                    name=name,
                    version=version,
                    ecosystem="npm",
                    category=category,
                    source_file=source_file,
                ))
        return results, warnings


class RequirementsParser(ManifestParser):

    _RE_LINE = re.compile(
        r"^\s*"
        r"([a-zA-Z0-9][\w\-.]*(?:\[[\w,\-]+\])?)"
        r"\s*"
        r"(?:"
        r"([><=!~]+)\s*([a-zA-Z0-9*._\-]+(?:\.\*)?)"
        r")?"
        r"\s*(?:#.*)?$"
    )

    _RE_EDITABLE = re.compile(
        r"^\s*-e\s+"
        r"(?:git|svn|hg|bzr)\+"
        r"([^#\s]+)"
        r"(?:#egg=([a-zA-Z_][\w.]*))?"
        r"\s*$"
    )

    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        results: list[_RawDependency] = []
        warnings: list[str] = []

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            m = self._RE_EDITABLE.match(stripped)
            if m:
                name = m.group(2)
                if name:
                    results.append(_RawDependency(
                        name=name,
                        version=None,
                        ecosystem="pip",
                        category="runtime",
                        source_file=source_file,
                    ))
                continue

            if stripped.startswith("-"):
                continue

            m = self._RE_LINE.match(stripped)
            if m:
                name = m.group(1)
                op = m.group(2)
                ver = m.group(3)
                version = f"{op}{ver}" if op and ver else None
                results.append(_RawDependency(
                    name=name,
                    version=version,
                    ecosystem="pip",
                    category="runtime",
                    source_file=source_file,
                ))
            else:
                warnings.append(f"{source_file}: unrecognized line: {stripped}")

        return results, warnings


class PyProjectParser(ManifestParser):

    _PEP508_RE = re.compile(
        r"^\s*"
        r"([a-zA-Z0-9][\w\-.]*(?:\[[\w,\-]+\])?)"
        r"\s*"
        r"(?:"
        r"([><=!~]+)\s*([a-zA-Z0-9*._\-]+)"
        r")?"
    )

    def _parse_pep508(self, entry: str, source_file: str) -> _RawDependency | None:
        entry = entry.strip()
        if not entry or entry.startswith("#"):
            return None
        parts = entry.split(";")
        base = parts[0].strip()
        m = self._PEP508_RE.match(base)
        if m:
            name = m.group(1)
            op = m.group(2)
            ver = m.group(3)
            version = f"{op}{ver}" if op and ver else None
            return _RawDependency(
                name=name,
                version=version,
                ecosystem="python",
                category="runtime",
                source_file=source_file,
            )
        return None

    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        warnings: list[str] = []
        try:
            import tomllib
            data = tomllib.loads(text)
        except Exception as exc:
            warnings.append(f"{source_file}: invalid TOML ({exc})")
            return [], warnings

        results: list[_RawDependency] = []

        deps = data.get("project", {})
        if isinstance(deps, dict):
            runtime_deps = deps.get("dependencies", [])
            if isinstance(runtime_deps, list):
                for entry in runtime_deps:
                    dep = self._parse_pep508(entry, source_file)
                    if dep:
                        results.append(dep)

            opt_deps = deps.get("optional-dependencies", {})
            if isinstance(opt_deps, dict):
                for group_name, group_deps in opt_deps.items():
                    if isinstance(group_deps, list):
                        for entry in group_deps:
                            dep = self._parse_pep508(entry, source_file)
                            if dep:
                                results.append(_RawDependency(
                                    name=dep.name,
                                    version=dep.version,
                                    ecosystem=dep.ecosystem,
                                    category="optional",
                                    source_file=dep.source_file,
                                ))

        poetry = data.get("tool", {}).get("poetry", {})
        if isinstance(poetry, dict):
            runtime_deps = poetry.get("dependencies", {})
            if isinstance(runtime_deps, dict):
                for name, specifier in runtime_deps.items():
                    if isinstance(specifier, str) and name != "python":
                        results.append(_RawDependency(
                            name=name,
                            version=specifier,
                            ecosystem="python",
                            category="runtime",
                            source_file=source_file,
                        ))
                    elif isinstance(specifier, dict):
                        version = specifier.get("version", None)
                        results.append(_RawDependency(
                            name=name,
                            version=version,
                            ecosystem="python",
                            category="runtime",
                            source_file=source_file,
                        ))

            dev_deps = poetry.get("dev-dependencies", {})
            if isinstance(dev_deps, dict):
                for name, specifier in dev_deps.items():
                    if isinstance(specifier, str):
                        results.append(_RawDependency(
                            name=name,
                            version=specifier,
                            ecosystem="python",
                            category="development",
                            source_file=source_file,
                        ))
                    elif isinstance(specifier, dict):
                        version = specifier.get("version", None)
                        results.append(_RawDependency(
                            name=name,
                            version=version,
                            ecosystem="python",
                            category="development",
                            source_file=source_file,
                        ))

            groups = poetry.get("group", {})
            if isinstance(groups, dict):
                for group_name, group_cfg in groups.items():
                    group_deps = group_cfg.get("dependencies", {}) if isinstance(group_cfg, dict) else {}
                    cat = "development" if group_name == "dev" else "optional"
                    if isinstance(group_deps, dict):
                        for name, specifier in group_deps.items():
                            if isinstance(specifier, str):
                                results.append(_RawDependency(
                                    name=name,
                                    version=specifier,
                                    ecosystem="python",
                                    category=cat,
                                    source_file=source_file,
                                ))
                            elif isinstance(specifier, dict):
                                version = specifier.get("version", None)
                                results.append(_RawDependency(
                                    name=name,
                                    version=version,
                                    ecosystem="python",
                                    category=cat,
                                    source_file=source_file,
                                ))

        return results, warnings


class PomParser(ManifestParser):

    _CATEGORY_MAP = {
        "compile": "runtime",
        "runtime": "runtime",
        "provided": "runtime",
        "test": "development",
        "system": "system",
    }

    def _namespaces(self, element: ET.Element) -> dict[str, str]:
        ns: dict[str, str] = {}
        for e in element.iter():
            if e.tag[0] == "{":
                uri = e.tag[1:].split("}")[0]
                prefix = uri.split("/")[-1].split(".")[-1].lower()
                if prefix not in ns:
                    ns[prefix] = uri
        return ns

    def _tag(self, ns: dict[str, str], name: str) -> str:
        for prefix, uri in ns.items():
            return f"{{{uri}}}{name}"
        return name

    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        warnings: list[str] = []
        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            warnings.append(f"{source_file}: invalid XML ({exc})")
            return [], warnings

        ns = self._namespaces(root)
        results: list[_RawDependency] = []

        for dep in root.iter(self._tag(ns, "dependency")):
            group_id_el = dep.find(self._tag(ns, "groupId"))
            artifact_id_el = dep.find(self._tag(ns, "artifactId"))
            version_el = dep.find(self._tag(ns, "version"))
            scope_el = dep.find(self._tag(ns, "scope"))
            optional_el = dep.find(self._tag(ns, "optional"))

            if group_id_el is None or artifact_id_el is None:
                continue

            group = group_id_el.text or ""
            artifact = artifact_id_el.text or ""
            name = f"{group}:{artifact}"
            version = version_el.text if version_el is not None else None

            scope = scope_el.text if scope_el is not None else "compile"
            category = self._CATEGORY_MAP.get(scope, "runtime")

            if optional_el is not None and optional_el.text and optional_el.text.strip().lower() == "true":
                category = "optional"

            if not artifact:
                continue

            results.append(_RawDependency(
                name=name,
                version=version,
                ecosystem="maven",
                category=category,
                source_file=source_file,
            ))

        return results, warnings


class GradleParser(ManifestParser):

    _RE_DEP = re.compile(
        r"(?P<config>"
        r"implementation|api|compileOnly|runtimeOnly"
        r"|testImplementation|testCompileOnly|testRuntimeOnly"
        r"|compile|testCompile|runtime|testRuntime"
        r"|annotationProcessor|kapt"
        r")"
        r"\s*[\(]\s*"
        r"[\"']"
        r"(?P<group>[^:]+)"
        r":"
        r"(?P<artifact>[^:]+)"
        r"(?::(?P<version>[^\"']+))?"
        r"[\"']\s*[\)]?"
    )

    _RE_DEP_NO_PARENS = re.compile(
        r"(?P<config>"
        r"implementation|api|compileOnly|runtimeOnly"
        r"|testImplementation|testCompileOnly|testRuntimeOnly"
        r"|compile|testCompile|runtime|testRuntime"
        r"|annotationProcessor|kapt"
        r")"
        r"\s+"
        r"[\"']"
        r"(?P<group>[^:]+)"
        r":"
        r"(?P<artifact>[^:]+)"
        r"(?::(?P<version>[^\"']+))?"
        r"[\"']"
    )

    _CATEGORY_MAP: dict[str, str] = {
        "implementation": "runtime",
        "api": "runtime",
        "compile": "runtime",
        "runtime": "runtime",
        "runtimeOnly": "runtime",
        "compileOnly": "build",
        "testImplementation": "development",
        "testCompile": "development",
        "testCompileOnly": "development",
        "testRuntime": "development",
        "testRuntimeOnly": "development",
        "annotationProcessor": "build",
        "kapt": "build",
    }

    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        results: list[_RawDependency] = []
        warnings: list[str] = []

        for pattern in (self._RE_DEP, self._RE_DEP_NO_PARENS):
            for m in pattern.finditer(text):
                config = m.group("config")
                group = m.group("group")
                artifact = m.group("artifact")
                version = m.group("version")
                name = f"{group}:{artifact}"
                category = self._CATEGORY_MAP.get(config, "runtime")
                results.append(_RawDependency(
                    name=name,
                    version=version,
                    ecosystem="gradle",
                    category=category,
                    source_file=source_file,
                ))

        if not results:
            warnings.append(f"{source_file}: no dependencies matched (Gradle DSL parsing is best-effort)")

        return results, warnings


class CargoParser(ManifestParser):

    _CATEGORY_MAP = {
        "dependencies": "runtime",
        "dev-dependencies": "development",
        "build-dependencies": "build",
    }

    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        warnings: list[str] = []
        try:
            import tomllib
            data = tomllib.loads(text)
        except Exception as exc:
            warnings.append(f"{source_file}: invalid TOML ({exc})")
            return [], warnings

        results: list[_RawDependency] = []

        for section, category in self._CATEGORY_MAP.items():
            entries = data.get(section, {})
            if not isinstance(entries, dict):
                continue
            for name, specifier in entries.items():
                if isinstance(specifier, str):
                    version = specifier
                elif isinstance(specifier, dict):
                    version = specifier.get("version", None)
                    if not version:
                        if "git" in specifier or "path" in specifier or "workspace" in specifier:
                            version = None
                        else:
                            version = None
                else:
                    version = None
                results.append(_RawDependency(
                    name=name,
                    version=version,
                    ecosystem="cargo",
                    category=category,
                    source_file=source_file,
                ))

        return results, warnings


class ComposerParser(ManifestParser):

    _CATEGORY_MAP = {
        "require": "runtime",
        "require-dev": "development",
    }

    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        warnings: list[str] = []
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            warnings.append(f"{source_file}: invalid JSON ({exc})")
            return [], warnings
        if not isinstance(data, dict):
            warnings.append(f"{source_file}: root value is not an object")
            return [], warnings

        results: list[_RawDependency] = []
        for section, category in self._CATEGORY_MAP.items():
            entries = data.get(section, {})
            if not isinstance(entries, dict):
                continue
            for name, specifier in entries.items():
                version = specifier if isinstance(specifier, str) else None
                results.append(_RawDependency(
                    name=name,
                    version=version,
                    ecosystem="packagist",
                    category=category,
                    source_file=source_file,
                ))

        return results, warnings


class GemfileParser(ManifestParser):

    _RE_GEM = re.compile(
        r"^\s*gem\s+"
        r"[\"']"
        r"(?P<name>[a-zA-Z0-9_\-]+)"
        r"[\"']"
        r"(?:\s*[,>=\s]*\s*[\"'](?P<version>[^\"']+)[\"'])?"
        r"\s*$"
    )

    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        results: list[_RawDependency] = []
        warnings: list[str] = []

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            m = self._RE_GEM.match(stripped)
            if m:
                name = m.group("name")
                version = m.group("version")
                results.append(_RawDependency(
                    name=name,
                    version=version,
                    ecosystem="rubygems",
                    category="runtime",
                    source_file=source_file,
                ))

        return results, warnings


class CsProjParser(ManifestParser):

    def _namespaces(self, element: ET.Element) -> dict[str, str]:
        ns: dict[str, str] = {}
        for e in element.iter():
            if e.tag[0] == "{":
                uri = e.tag[1:].split("}")[0]
                prefix = uri.split("/")[-1].split(".")[-1].lower()
                if prefix not in ns:
                    ns[prefix] = uri
        return ns

    def _tag(self, ns: dict[str, str], name: str) -> str:
        for prefix, uri in ns.items():
            return f"{{{uri}}}{name}"
        return name

    def parse(self, text: str, source_file: str) -> tuple[list[_RawDependency], list[str]]:
        warnings: list[str] = []
        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            warnings.append(f"{source_file}: invalid XML ({exc})")
            return [], warnings

        ns = self._namespaces(root)
        results: list[_RawDependency] = []

        for ref in root.iter(self._tag(ns, "PackageReference")):
            include = ref.get("Include")
            version = ref.get("Version")
            if not include:
                continue
            results.append(_RawDependency(
                name=include,
                version=version,
                ecosystem="nuget",
                category="runtime",
                source_file=source_file,
            ))

        return results, warnings


_PARSER_REGISTRY: dict[str, list[type[ManifestParser]]] = {
    "package.json": [PackageJsonParser],
    "requirements.txt": [RequirementsParser],
    "pyproject.toml": [PyProjectParser],
    "pom.xml": [PomParser],
    "build.gradle": [GradleParser],
    "build.gradle.kts": [GradleParser],
    "composer.json": [ComposerParser],
    "Cargo.toml": [CargoParser],
    "Gemfile": [GemfileParser],
    "*.csproj": [CsProjParser],
}


def _resolve_parsers(filename: str) -> list[type[ManifestParser]]:
    parsers = _PARSER_REGISTRY.get(filename)
    if parsers is not None:
        return parsers
    if filename.endswith(".csproj"):
        return [CsProjParser]
    return []


def _merge_deduplicate(
    raw_deps: list[_RawDependency],
) -> tuple[list[DetectedDependency], list[str]]:
    groups: dict[tuple[str, str, str], dict] = {}
    warnings: list[str] = []

    for dep in raw_deps:
        key = (dep.name, dep.ecosystem, dep.category)
        existing = groups.get(key)
        if existing is None:
            groups[key] = {
                "name": dep.name,
                "version": dep.version,
                "ecosystem": dep.ecosystem,
                "category": dep.category,
                "source_files": {dep.source_file},
            }
        else:
            existing["source_files"].add(dep.source_file)
            if dep.version is not None and existing["version"] is not None and dep.version != existing["version"]:
                warnings.append(
                    f"Version conflict for {dep.name} ({dep.ecosystem}/{dep.category}): "
                    f"{existing['version']} vs {dep.version}"
                )
            elif dep.version is not None and existing["version"] is None:
                existing["version"] = dep.version

    merged = []
    for key, acc in sorted(groups.items(), key=lambda x: (x[1]["name"], x[1]["ecosystem"], x[1]["category"])):
        merged.append(DetectedDependency(
            name=acc["name"],
            version=acc["version"],
            ecosystem=acc["ecosystem"],
            category=acc["category"],
            source_files=tuple(sorted(acc["source_files"])),
        ))

    return merged, warnings


class DependencyDetector(BaseDetector):

    def detect(self, context: DiscoveryContext) -> DetectorResult:
        try:
            return self._detect(context)
        except Exception as exc:
            self._logger.exception("Dependency detection failed")
            return DetectorResult(
                detector_name=self.detector_name,
                error=f"{type(exc).__name__}: {exc}",
            )

    def _detect(self, context: DiscoveryContext) -> DetectorResult:
        all_raw: list[_RawDependency] = []
        all_warnings: list[str] = []

        for node in context.file_graph.files:
            parsers = _resolve_parsers(node.file_name)
            if not parsers:
                continue
            content = self._read_manifest(context, node.relative_path)
            if content is None:
                all_warnings.append(f"{node.relative_path}: unreadable")
                continue
            for parser_cls in parsers:
                parser = parser_cls()
                raw_deps, warnings = parser.parse(content, node.relative_path)
                all_raw.extend(raw_deps)
                all_warnings.extend(warnings)

        if not all_raw:
            all_warnings.append("No dependencies found")

        merged, merge_warnings = _merge_deduplicate(all_raw)
        all_warnings.extend(merge_warnings)

        return DetectorResult(
            detector_name=self.detector_name,
            dependencies=tuple(merged),
        )

    def _read_manifest(self, context: DiscoveryContext, relative_path: str) -> str | None:
        root = getattr(context, "root_path", None)
        if root is None:
            return None
        full = root / relative_path
        try:
            return full.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            return None

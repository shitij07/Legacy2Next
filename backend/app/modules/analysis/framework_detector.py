import json
import re
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from app.modules.analysis.base import BaseDetector
from app.modules.analysis.types import (
    DetectedTechnology,
    DetectorResult,
    DiscoveryContext,
)


@dataclass(frozen=True)
class Evidence:
    confidence: str
    detail: str


class EvidenceRule(ABC):

    @abstractmethod
    def evaluate(self, context: DiscoveryContext) -> Evidence | None:
        ...


class JsonDependencyRule(EvidenceRule):
    """Check for a dependency at a dot-separated path in a JSON file."""

    def __init__(self, filename: str, key_path: str):
        self.filename = filename
        self.key_path = key_path

    def evaluate(self, context: DiscoveryContext) -> Evidence | None:
        node = _find_file(context, self.filename)
        if node is None:
            return None
        content = _read_text(context, node.relative_path)
        if content is None:
            return Evidence("medium", f"{self.filename} (unreadable)")
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return Evidence("medium", f"{self.filename} (corrupt)")
        parts = self.key_path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        if current is not None:
            return Evidence("high", f"{self.filename} → {self.key_path}")
        return None


class XmlDependencyRule(EvidenceRule):
    """Check for a dependency artifactId prefix in an XML file (pom.xml, csproj)."""

    def __init__(self, filename: str, artifact_prefix: str):
        self.filename = filename
        self.artifact_prefix = artifact_prefix

    def evaluate(self, context: DiscoveryContext) -> Evidence | None:
        node = _find_file(context, self.filename)
        if node is None:
            return None
        content = _read_text(context, node.relative_path)
        if content is None:
            return Evidence("medium", f"{self.filename} (unreadable)")
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return Evidence("medium", f"{self.filename} (corrupt)")
        ns = _namespaces(root)
        for artifact in root.iter(_tag(ns, "artifactId")):
            if artifact.text and artifact.text.startswith(self.artifact_prefix):
                return Evidence("high", f"{self.filename} → {artifact.text}")
        return None


class TomlDependencyRule(EvidenceRule):
    """Check for a dependency at a dot-separated path in a TOML file."""

    def __init__(self, filename: str, key_path: str):
        self.filename = filename
        self.key_path = key_path

    def evaluate(self, context: DiscoveryContext) -> Evidence | None:
        node = _find_file(context, self.filename)
        if node is None:
            return None
        content = _read_text(context, node.relative_path)
        if content is None:
            return Evidence("medium", f"{self.filename} (unreadable)")
        try:
            import tomllib
            data = tomllib.loads(content)
        except Exception:
            return Evidence("medium", f"{self.filename} (corrupt)")
        parts = self.key_path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        if current is not None:
            return Evidence("high", f"{self.filename} → {self.key_path}")
        return None


class LineDependencyRule(EvidenceRule):
    """Check for a package reference in a line-based dependency file."""

    def __init__(self, filename: str, pattern: str):
        self.filename = filename
        self.pattern = pattern.lower()

    def evaluate(self, context: DiscoveryContext) -> Evidence | None:
        node = _find_file(context, self.filename)
        if node is None:
            return None
        content = _read_text(context, node.relative_path)
        if content is None:
            return Evidence("medium", f"{self.filename} (unreadable)")
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue
            lower = stripped.lower()
            if lower.startswith(self.pattern):
                return Evidence("high", f"{self.filename} → {self.pattern}")
            match = re.match(r'^\s*gem\s+[\'"](' + re.escape(self.pattern) + r')[\'"]', line)
            if match:
                return Evidence("high", f"{self.filename} → {match.group(1)}")
        return None


class FileExistsRule(EvidenceRule):
    """Check if a known evidence file exists."""

    def __init__(self, filename: str):
        self.filename = filename

    def evaluate(self, context: DiscoveryContext) -> Evidence | None:
        node = _find_file(context, self.filename)
        if node is None:
            return None
        return Evidence("medium", self.filename)


@dataclass(frozen=True)
class FrameworkDefinition:
    name: str
    category: str
    rules: list[EvidenceRule] = field(default_factory=list)


FRAMEWORK_DEFINITIONS: list[FrameworkDefinition] = [
    # ── Frontend Frameworks ──
    FrameworkDefinition("React", "framework", [
        JsonDependencyRule("package.json", "dependencies.react"),
        JsonDependencyRule("package.json", "devDependencies.react"),
    ]),
    FrameworkDefinition("Next.js", "framework", [
        JsonDependencyRule("package.json", "dependencies.next"),
        FileExistsRule("next.config.js"),
        FileExistsRule("next.config.mjs"),
    ]),
    FrameworkDefinition("Vue", "framework", [
        JsonDependencyRule("package.json", "dependencies.vue"),
        JsonDependencyRule("package.json", "devDependencies.vue"),
    ]),
    FrameworkDefinition("Nuxt", "framework", [
        JsonDependencyRule("package.json", "dependencies.nuxt"),
        FileExistsRule("nuxt.config.ts"),
        FileExistsRule("nuxt.config.js"),
    ]),
    FrameworkDefinition("Angular", "framework", [
        JsonDependencyRule("package.json", "dependencies.@angular/core"),
        JsonDependencyRule("package.json", "devDependencies.@angular/core"),
        FileExistsRule("angular.json"),
    ]),
    FrameworkDefinition("Svelte", "framework", [
        JsonDependencyRule("package.json", "dependencies.svelte"),
        JsonDependencyRule("package.json", "devDependencies.svelte"),
    ]),
    FrameworkDefinition("SvelteKit", "framework", [
        JsonDependencyRule("package.json", "dependencies.@sveltejs/kit"),
        JsonDependencyRule("package.json", "devDependencies.@sveltejs/kit"),
        FileExistsRule("svelte.config.js"),
    ]),

    # ── Backend Frameworks ──
    FrameworkDefinition("Express", "framework", [
        JsonDependencyRule("package.json", "dependencies.express"),
        JsonDependencyRule("package.json", "devDependencies.express"),
    ]),
    FrameworkDefinition("NestJS", "framework", [
        JsonDependencyRule("package.json", "dependencies.@nestjs/core"),
        JsonDependencyRule("package.json", "devDependencies.@nestjs/core"),
    ]),
    FrameworkDefinition("Django", "framework", [
        LineDependencyRule("requirements.txt", "django"),
        TomlDependencyRule("pyproject.toml", "tool.poetry.dependencies.django"),
        TomlDependencyRule("pyproject.toml", "project.dependencies.django"),
        FileExistsRule("manage.py"),
    ]),
    FrameworkDefinition("Flask", "framework", [
        LineDependencyRule("requirements.txt", "flask"),
        TomlDependencyRule("pyproject.toml", "tool.poetry.dependencies.flask"),
        TomlDependencyRule("pyproject.toml", "project.dependencies.flask"),
    ]),
    FrameworkDefinition("FastAPI", "framework", [
        LineDependencyRule("requirements.txt", "fastapi"),
        TomlDependencyRule("pyproject.toml", "tool.poetry.dependencies.fastapi"),
        TomlDependencyRule("pyproject.toml", "project.dependencies.fastapi"),
    ]),
    FrameworkDefinition("Spring Boot", "framework", [
        XmlDependencyRule("pom.xml", "spring-boot-starter"),
        XmlDependencyRule("build.gradle", "spring-boot"),
        FileExistsRule("build.gradle"),
        FileExistsRule("build.gradle.kts"),
    ]),
    FrameworkDefinition("ASP.NET Core", "framework", [
        XmlDependencyRule("*.csproj", "Microsoft.AspNetCore"),
        FileExistsRule("Program.cs"),
    ]),
    FrameworkDefinition("Laravel", "framework", [
        JsonDependencyRule("composer.json", "require.laravel/framework"),
        FileExistsRule("artisan"),
    ]),
    FrameworkDefinition("Ruby on Rails", "framework", [
        LineDependencyRule("Gemfile", "rails"),
    ]),

    # ── Build Tools ──
    FrameworkDefinition("Vite", "build_tool", [
        JsonDependencyRule("package.json", "devDependencies.vite"),
        FileExistsRule("vite.config.ts"),
        FileExistsRule("vite.config.js"),
    ]),
    FrameworkDefinition("Webpack", "build_tool", [
        JsonDependencyRule("package.json", "devDependencies.webpack"),
        FileExistsRule("webpack.config.js"),
    ]),
    FrameworkDefinition("Rollup", "build_tool", [
        JsonDependencyRule("package.json", "devDependencies.rollup"),
        FileExistsRule("rollup.config.js"),
    ]),
    FrameworkDefinition("Parcel", "build_tool", [
        JsonDependencyRule("package.json", "devDependencies.parcel"),
        FileExistsRule(".parcelrc"),
    ]),
    FrameworkDefinition("Maven", "build_tool", [
        FileExistsRule("pom.xml"),
    ]),
    FrameworkDefinition("Gradle", "build_tool", [
        FileExistsRule("build.gradle"),
        FileExistsRule("build.gradle.kts"),
        FileExistsRule("gradlew"),
    ]),
    FrameworkDefinition("Cargo", "build_tool", [
        FileExistsRule("Cargo.toml"),
    ]),

    # ── Package Managers ──
    FrameworkDefinition("npm", "package_manager", [
        FileExistsRule("package-lock.json"),
    ]),
    FrameworkDefinition("pnpm", "package_manager", [
        FileExistsRule("pnpm-lock.yaml"),
    ]),
    FrameworkDefinition("yarn", "package_manager", [
        FileExistsRule("yarn.lock"),
    ]),
    FrameworkDefinition("bun", "package_manager", [
        FileExistsRule("bun.lockb"),
    ]),
    FrameworkDefinition("pip", "package_manager", [
        FileExistsRule("requirements.txt"),
    ]),
    FrameworkDefinition("Poetry", "package_manager", [
        FileExistsRule("poetry.lock"),
        TomlDependencyRule("pyproject.toml", "tool.poetry"),
    ]),

    # ── Runtimes ──
    FrameworkDefinition("Node.js", "runtime", [
        FileExistsRule("package.json"),
    ]),
    FrameworkDefinition("Deno", "runtime", [
        FileExistsRule("deno.json"),
        FileExistsRule("deno.jsonc"),
    ]),
    FrameworkDefinition("Bun", "runtime", [
        FileExistsRule("bun.lockb"),
        FileExistsRule("bunfig.toml"),
    ]),
]


class FrameworkDetector(BaseDetector):

    def detect(self, context: DiscoveryContext) -> DetectorResult:
        try:
            return self._detect(context)
        except Exception as exc:
            self._logger.exception("Framework detection failed")
            return DetectorResult(
                detector_name=self.detector_name,
                error=f"{type(exc).__name__}: {exc}",
            )

    def _detect(self, context: DiscoveryContext) -> DetectorResult:
        technologies: dict[str, _TechAccum] = {}

        for definition in FRAMEWORK_DEFINITIONS:
            best_conf: str | None = None
            details: list[str] = []

            for rule in definition.rules:
                evidence = rule.evaluate(context)
                if evidence is None:
                    continue
                if best_conf is None or _conf_level(evidence.confidence) > _conf_level(best_conf):
                    best_conf = evidence.confidence
                if evidence.detail not in details:
                    details.append(evidence.detail)

            if best_conf is None:
                continue

            acc = technologies.get(definition.name)
            if acc is not None:
                if _conf_level(best_conf) > _conf_level(acc.confidence):
                    acc = _TechAccum(definition.name, definition.category, best_conf, acc.details)
                for d in details:
                    if d not in acc.details:
                        acc.details.append(d)
                technologies[definition.name] = acc
            else:
                technologies[definition.name] = _TechAccum(
                    definition.name, definition.category, best_conf, details,
                )

        result_technologies = tuple(
            DetectedTechnology(
                name=acc.name,
                category=acc.category,
                evidence=", ".join(acc.details),
                confidence=acc.confidence,
            )
            for acc in sorted(technologies.values(), key=lambda x: x.name)
        )

        return DetectorResult(
            detector_name=self.detector_name,
            technologies=result_technologies,
        )


@dataclass
class _TechAccum:
    name: str
    category: str
    confidence: str
    details: list[str]


def _conf_level(confidence: str) -> int:
    return {"high": 2, "medium": 1, "low": 0}.get(confidence, 0)


def _find_file(context: DiscoveryContext, name: str) -> "FileNode | None":
    from app.modules.analysis.types import FileNode
    if name.startswith("*."):
        ext = name[1:]
        for f in context.file_graph.files:
            if f.file_name.endswith(ext):
                return f
        return None
    matches = context.file_graph.find_files_by_name(name)
    return matches[0] if matches else None


def _read_text(context: DiscoveryContext, relative_path: str) -> str | None:
    root = getattr(context, "root_path", None)
    if root is None:
        return None
    full: Path = root / relative_path
    try:
        return full.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None


def _namespaces(element: ET.Element) -> dict[str, str]:
    ns: dict[str, str] = {}
    for e in element.iter():
        if e.tag[0] == "{":
            uri = e.tag[1:].split("}")[0]
            prefix = uri.split("/")[-1].split(".")[-1].lower()
            if prefix not in ns:
                ns[prefix] = uri
    return ns


def _tag(ns: dict[str, str], name: str) -> str:
    for prefix, uri in ns.items():
        return f"{{{uri}}}{name}"
    return name

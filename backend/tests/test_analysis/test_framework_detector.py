import json
import tempfile
from pathlib import Path

import pytest

from app.modules.analysis.discovery import DiscoveryEngine
from app.modules.analysis.framework_detector import (
    FRAMEWORK_DEFINITIONS,
    Evidence,
    FileExistsRule,
    FrameworkDetector,
    JsonDependencyRule,
    LineDependencyRule,
    TomlDependencyRule,
    XmlDependencyRule,
)
from app.modules.analysis.types import DiscoveryContext


def _create_project(root: Path, structure: dict[str, str | None]) -> None:
    for path, content in structure.items():
        full = root / path
        if content is None:
            full.mkdir(parents=True, exist_ok=True)
        else:
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")


def _discover(root: Path) -> DiscoveryContext:
    return DiscoveryEngine().discover(
        root_path=root,
        upload_id=1,
        project_id=1,
    )


# ─── EvidenceRule Tests ──────────────────────────────────────────────────


class TestJsonDependencyRule:

    def test_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"package.json": json.dumps({"dependencies": {"react": "^18.0.0"}})})
            ctx = _discover(root)
            rule = JsonDependencyRule("package.json", "dependencies.react")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "high"
        assert "react" in ev.detail

    def test_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"package.json": json.dumps({"dependencies": {"vue": "^3.0.0"}})})
            ctx = _discover(root)
            rule = JsonDependencyRule("package.json", "dependencies.react")
            ev = rule.evaluate(ctx)
        assert ev is None

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            rule = JsonDependencyRule("package.json", "dependencies.react")
            ev = rule.evaluate(ctx)
        assert ev is None

    def test_corrupt_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"package.json": "not valid json"})
            ctx = _discover(root)
            rule = JsonDependencyRule("package.json", "dependencies.react")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "medium"
        assert "corrupt" in ev.detail

    def test_deeply_nested(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"package.json": json.dumps({"devDependencies": {"@angular/core": "^15.0.0"}})})
            ctx = _discover(root)
            rule = JsonDependencyRule("package.json", "devDependencies.@angular/core")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "high"

    def test_intermediate_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"package.json": json.dumps({"scripts": {"build": "vite build"}})})
            ctx = _discover(root)
            rule = JsonDependencyRule("package.json", "dependencies.react")
            ev = rule.evaluate(ctx)
        assert ev is None


class TestXmlDependencyRule:

    def test_found_pom_xml(self):
        pom = """<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
  </dependencies>
</project>"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"pom.xml": pom})
            ctx = _discover(root)
            rule = XmlDependencyRule("pom.xml", "spring-boot-starter")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "high"

    def test_not_found(self):
        pom = """<?xml version="1.0"?>
<project>
  <dependencies>
    <dependency>
      <artifactId>junit</artifactId>
    </dependency>
  </dependencies>
</project>"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"pom.xml": pom})
            ctx = _discover(root)
            rule = XmlDependencyRule("pom.xml", "spring-boot-starter")
            ev = rule.evaluate(ctx)
        assert ev is None

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            rule = XmlDependencyRule("pom.xml", "spring-boot-starter")
            ev = rule.evaluate(ctx)
        assert ev is None

    def test_corrupt_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"pom.xml": "not valid xml"})
            ctx = _discover(root)
            rule = XmlDependencyRule("pom.xml", "spring-boot-starter")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "medium"
        assert "corrupt" in ev.detail

    def test_wildcard_filename(self):
        pom = """<project>
  <dependencies>
    <dependency>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
  </dependencies>
</project>"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"pom.xml": pom})
            ctx = _discover(root)
            rule = XmlDependencyRule("pom.xml", "spring-boot-starter")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "high"

    def test_csproj_not_found(self):
        csproj = """<Project Sdk="Microsoft.NET.Sdk.Web">
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.0" />
  </ItemGroup>
</Project>"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"app.csproj": csproj})
            ctx = _discover(root)
            rule = XmlDependencyRule("*.csproj", "Microsoft.AspNetCore")
            ev = rule.evaluate(ctx)
        assert ev is None


class TestTomlDependencyRule:

    def test_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"Cargo.toml": '[dependencies]\nactix-web = "4.0"'})
            ctx = _discover(root)
            rule = TomlDependencyRule("Cargo.toml", "dependencies.actix-web")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "high"

    def test_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"Cargo.toml": '[dependencies]\nserde = "1.0"'})
            ctx = _discover(root)
            rule = TomlDependencyRule("Cargo.toml", "dependencies.actix-web")
            ev = rule.evaluate(ctx)
        assert ev is None

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            rule = TomlDependencyRule("Cargo.toml", "dependencies.actix-web")
            ev = rule.evaluate(ctx)
        assert ev is None

    def test_corrupt_toml(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"Cargo.toml": "[[[invalid"})
            ctx = _discover(root)
            rule = TomlDependencyRule("Cargo.toml", "dependencies.actix-web")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "medium"

    def test_pyproject_toml_poetry(self):
        toml = """[tool.poetry.dependencies]
fastapi = "^0.104.0"
python = "^3.11"
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"pyproject.toml": toml})
            ctx = _discover(root)
            rule = TomlDependencyRule("pyproject.toml", "tool.poetry.dependencies.fastapi")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "high"

    def test_pyproject_toml_pep621(self):
        toml = """[project.dependencies]
fastapi = "^0.104.0"
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"pyproject.toml": toml})
            ctx = _discover(root)
            rule = TomlDependencyRule("pyproject.toml", "project.dependencies.fastapi")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "high"


class TestLineDependencyRule:

    def test_found_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"requirements.txt": "django==4.2\nflask>=2.0"})
            ctx = _discover(root)
            rule = LineDependencyRule("requirements.txt", "django")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "high"

    def test_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"requirements.txt": "flask>=2.0\nrequests==2.31"})
            ctx = _discover(root)
            rule = LineDependencyRule("requirements.txt", "django")
            ev = rule.evaluate(ctx)
        assert ev is None

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            rule = LineDependencyRule("requirements.txt", "django")
            ev = rule.evaluate(ctx)
        assert ev is None

    def test_gemfile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"Gemfile": "gem 'rails', '~> 7.0'\ngem 'pg'"})
            ctx = _discover(root)
            rule = LineDependencyRule("Gemfile", "rails")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "high"

    def test_gemfile_double_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"Gemfile": 'gem "rails", "~> 7.0"'})
            ctx = _discover(root)
            rule = LineDependencyRule("Gemfile", "rails")
            ev = rule.evaluate(ctx)
        assert ev is not None

    def test_commented_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"requirements.txt": "# django\nflask"})
            ctx = _discover(root)
            rule = LineDependencyRule("requirements.txt", "django")
            ev = rule.evaluate(ctx)
        assert ev is None


class TestFileExistsRule:

    def test_file_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"angular.json": "{}"})
            ctx = _discover(root)
            rule = FileExistsRule("angular.json")
            ev = rule.evaluate(ctx)
        assert ev is not None
        assert ev.confidence == "medium"
        assert ev.detail == "angular.json"

    def test_file_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            rule = FileExistsRule("angular.json")
            ev = rule.evaluate(ctx)
        assert ev is None


# ─── FrameworkDetector Integration Tests ────────────────────────────────


class TestFrameworkDetector:

    _REACT_PACKAGE = json.dumps({"dependencies": {"react": "^18.0.0"}})
    _VUE_PACKAGE = json.dumps({"dependencies": {"vue": "^3.0.0"}})
    _ANGULAR_DEPS = json.dumps({"dependencies": {"@angular/core": "^15.0.0"}})

    def test_empty_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            result = FrameworkDetector().detect(ctx)
        assert result.error is None
        assert result.technologies == ()

    def test_react_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"package.json": self._REACT_PACKAGE})
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "React" in names
        assert "Node.js" in names  # package.json exists
        react = [t for t in result.technologies if t.name == "React"][0]
        assert react.category == "framework"
        assert react.confidence == "high"

    def test_multiple_frontend_frameworks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"package.json": json.dumps({
                "dependencies": {"react": "^18.0.0", "vue": "^3.0.0"},
            })})
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "React" in names
        assert "Vue" in names

    def test_angular_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": self._ANGULAR_DEPS,
                "angular.json": "{}",
            })
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        angular = [t for t in result.technologies if t.name == "Angular"][0]
        assert angular.confidence == "high"
        assert "angular.json" in angular.evidence

    def test_django_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "requirements.txt": "django==4.2\nflask>=2.0",
                "manage.py": "",
            })
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "Django" in names
        assert "Flask" in names
        assert "pip" in names  # requirements.txt exists

    def test_spring_boot_detected(self):
        pom = """<project xmlns="http://maven.apache.org/POM/4.0.0">
  <dependencies>
    <dependency>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
  </dependencies>
</project>"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"pom.xml": pom})
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "Spring Boot" in names
        assert "Maven" in names  # pom.xml exists

    def test_vite_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({"devDependencies": {"vite": "^5.0.0"}}),
                "vite.config.ts": "",
            })
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "Vite" in names
        vite = [t for t in result.technologies if t.name == "Vite"][0]
        assert vite.confidence == "high"

    def test_rust_cargo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"Cargo.toml": '[dependencies]\nserde = "1.0"'})
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "Cargo" in names

    def test_no_implied_technologies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({
                    "dependencies": {"next": "^14.0.0"},
                    "devDependencies": {},
                }),
                "next.config.js": "",
            })
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "Next.js" in names
        assert "React" not in names  # Next.js does NOT imply React

    def test_duplicate_evidence_merged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({
                    "dependencies": {"react": "^18.0.0"},
                    "devDependencies": {"react": "^18.0.0"},
                }),
            })
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        react = [t for t in result.technologies if t.name == "React"]
        assert len(react) == 1  # deduplicated

    def test_confidence_merging(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({
                    "dependencies": {"next": "^14.0.0"},
                }),
                "next.config.js": "",  # medium evidence
            })
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        nextjs = [t for t in result.technologies if t.name == "Next.js"][0]
        assert nextjs.confidence == "high"  # package.json → high wins

    def test_corrupted_config_medium_confidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"package.json": "corrupt json"})
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        node = [t for t in result.technologies if t.name == "Node.js"]
        assert len(node) == 1
        react = [t for t in result.technologies if t.name == "React"]
        assert len(react) == 1
        assert react[0].confidence == "medium"

    def test_deterministic_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({"dependencies": {"react": "^18.0.0", "vue": "^3.0.0"}}),
                "requirements.txt": "flask",
                "angular.json": "{}",
            })
            ctx = _discover(root)
            r1 = FrameworkDetector().detect(ctx)
            r2 = FrameworkDetector().detect(ctx)
        assert r1.technologies == r2.technologies

    def test_full_tech_stack(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({
                    "dependencies": {
                        "react": "^18.0.0",
                        "next": "^14.0.0",
                        "express": "^4.18.0",
                        "@nestjs/core": "^10.0.0",
                        "vue": "^3.0.0",
                        "@angular/core": "^15.0.0",
                        "svelte": "^4.0.0",
                    },
                    "devDependencies": {
                        "vite": "^5.0.0",
                        "webpack": "^5.0.0",
                        "rollup": "^4.0.0",
                        "parcel": "^2.0.0",
                    },
                }),
                "next.config.js": "",
                "vite.config.ts": "",
            })
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "React" in names
        assert "Next.js" in names
        assert "Express" in names
        assert "NestJS" in names
        assert "Vue" in names
        assert "Angular" in names
        assert "Svelte" in names
        assert "Vite" in names
        assert "Webpack" in names
        assert "Rollup" in names
        assert "Parcel" in names
        assert "Node.js" in names

    def test_bun_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"bun.lockb": ""})
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "Bun" in names  # runtime
        assert "bun" in names  # package manager

    def test_fastapi_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "pyproject.toml": '[tool.poetry.dependencies]\nfastapi = "^0.104.0"',
            })
            ctx = _discover(root)
            result = FrameworkDetector().detect(ctx)
        names = {t.name for t in result.technologies}
        assert "FastAPI" in names
        fastapi = [t for t in result.technologies if t.name == "FastAPI"][0]
        assert fastapi.confidence == "high"

    def test_detector_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            result = FrameworkDetector().detect(ctx)
        assert result.detector_name == "FrameworkDetector"

    def test_all_frameworks_have_category(self):
        for fd in FRAMEWORK_DEFINITIONS:
            assert fd.category in ("framework", "build_tool", "runtime", "package_manager"), fd.name

    def test_all_frameworks_have_rules(self):
        for fd in FRAMEWORK_DEFINITIONS:
            assert len(fd.rules) >= 1, fd.name

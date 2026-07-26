import json
import tempfile
from pathlib import Path

import pytest

from app.modules.analysis.dependency_detector import (
    ComposerParser,
    CsProjParser,
    CargoParser,
    DependencyDetector,
    GemfileParser,
    GradleParser,
    PackageJsonParser,
    PomParser,
    PyProjectParser,
    RequirementsParser,
    _RawDependency,
    _merge_deduplicate,
    _resolve_parsers,
)
from app.modules.analysis.discovery import DiscoveryEngine
from app.modules.analysis.types import DetectedDependency, DiscoveryContext


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


# ─── _RawDependency Tests ──────────────────────────────────────────────


class TestRawDependency:

    def test_creation(self):
        d = _RawDependency(name="requests", version="2.31.0", ecosystem="pip", category="runtime", source_file="requirements.txt")
        assert d.name == "requests"
        assert d.version == "2.31.0"

    def test_immutable(self):
        d = _RawDependency(name="flask", version=None, ecosystem="pip", category="runtime", source_file="requirements.txt")
        with pytest.raises((AttributeError, TypeError, Exception)):
            d.name = "django"  # type: ignore

    def test_no_version(self):
        d = _RawDependency(name="flask", version=None, ecosystem="pip", category="runtime", source_file="req.txt")
        assert d.version is None


# ─── PackageJsonParser Tests ────────────────────────────────────────────


class TestPackageJsonParser:

    def test_dependencies(self):
        text = '{"dependencies": {"react": "^18.0.0", "express": "^4.18.0"}}'
        deps, warns = PackageJsonParser().parse(text, "package.json")
        assert len(deps) == 2
        names = {d.name for d in deps}
        assert names == {"react", "express"}
        assert all(d.ecosystem == "npm" for d in deps)
        assert all(d.category == "runtime" for d in deps)
        assert warns == []

    def test_dev_dependencies(self):
        text = '{"devDependencies": {"vite": "^5.0.0"}}'
        deps, warns = PackageJsonParser().parse(text, "package.json")
        assert len(deps) == 1
        assert deps[0].name == "vite"
        assert deps[0].category == "development"

    def test_peer_dependencies(self):
        text = '{"peerDependencies": {"react": "^18.0.0"}}'
        deps, warns = PackageJsonParser().parse(text, "package.json")
        assert len(deps) == 1
        assert deps[0].category == "peer"

    def test_optional_dependencies(self):
        text = '{"optionalDependencies": {"fsevents": "^2.3.0"}}'
        deps, warns = PackageJsonParser().parse(text, "package.json")
        assert len(deps) == 1
        assert deps[0].category == "optional"

    def test_all_sections(self):
        text = json.dumps({
            "dependencies": {"react": "^18.0.0"},
            "devDependencies": {"vite": "^5.0.0"},
            "peerDependencies": {"react-dom": "^18.0.0"},
            "optionalDependencies": {"fsevents": "^2.3.0"},
        })
        deps, warns = PackageJsonParser().parse(text, "package.json")
        assert len(deps) == 4
        categories = {d.category for d in deps}
        assert categories == {"runtime", "development", "peer", "optional"}

    def test_empty_file(self):
        deps, warns = PackageJsonParser().parse("{}", "package.json")
        assert deps == []
        assert warns == []

    def test_corrupt_json(self):
        deps, warns = PackageJsonParser().parse("not json", "package.json")
        assert deps == []
        assert len(warns) == 1
        assert "invalid JSON" in warns[0]

    def test_non_object(self):
        deps, warns = PackageJsonParser().parse('"string"', "package.json")
        assert deps == []
        assert len(warns) == 1

    def test_no_dependency_sections(self):
        deps, warns = PackageJsonParser().parse('{"name": "test"}', "package.json")
        assert deps == []
        assert warns == []

    def test_dict_version_format(self):
        text = json.dumps({"dependencies": {"dep": {"version": "1.0.0", "extras": ["extra"]}}})
        deps, warns = PackageJsonParser().parse(text, "package.json")
        assert len(deps) == 1
        assert deps[0].version == "1.0.0"

    def test_deterministic_order(self):
        text = json.dumps({"dependencies": {"z": "1.0", "a": "2.0", "m": "3.0"}})
        deps, warns = PackageJsonParser().parse(text, "package.json")
        names = [d.name for d in deps]
        assert names == ["z", "a", "m"]


# ─── RequirementsParser Tests ──────────────────────────────────────────


class TestRequirementsParser:

    def test_pinned_version(self):
        text = "requests==2.31.0"
        deps, warns = RequirementsParser().parse(text, "requirements.txt")
        assert len(deps) == 1
        assert deps[0].name == "requests"
        assert deps[0].version == "==2.31.0"
        assert deps[0].ecosystem == "pip"

    def test_version_range(self):
        text = "flask>=2.0"
        deps, warns = RequirementsParser().parse(text, "requirements.txt")
        assert len(deps) == 1
        assert deps[0].version == ">=2.0"

    def test_no_version(self):
        text = "flask"
        deps, warns = RequirementsParser().parse(text, "requirements.txt")
        assert len(deps) == 1
        assert deps[0].version is None

    def test_comments_and_blank_lines(self):
        text = "# this is a comment\n\nrequests==2.31.0\n"
        deps, warns = RequirementsParser().parse(text, "requirements.txt")
        assert len(deps) == 1
        assert warns == []

    def test_options_skipped(self):
        text = "--index-url https://example.com\nrequests==2.31.0"
        deps, warns = RequirementsParser().parse(text, "requirements.txt")
        assert len(deps) == 1
        assert deps[0].name == "requests"

    def test_editable_git(self):
        text = "-e git+https://example.com/repo.git#egg=mypackage"
        deps, warns = RequirementsParser().parse(text, "requirements.txt")
        assert len(deps) == 1
        assert deps[0].name == "mypackage"
        assert deps[0].version is None

    def test_unrecognized_line(self):
        text = "|||invalid|||"
        deps, warns = RequirementsParser().parse(text, "requirements.txt")
        assert deps == []
        assert len(warns) == 1

    def test_multiple(self):
        text = "django==4.2\nflask>=2.0\nrequests\n"
        deps, warns = RequirementsParser().parse(text, "requirements.txt")
        assert len(deps) == 3

    def test_category_always_runtime(self):
        text = "pytest==7.0"
        deps, warns = RequirementsParser().parse(text, "requirements.txt")
        assert deps[0].category == "runtime"


# ─── PyProjectParser Tests ─────────────────────────────────────────────


class TestPyProjectParser:

    def test_pep621_dependencies(self):
        text = '[project]\ndependencies = ["requests>=2.28.0", "flask>=2.0"]'
        deps, warns = PyProjectParser().parse(text, "pyproject.toml")
        assert len(deps) == 2
        assert deps[0].ecosystem == "python"
        assert deps[0].category == "runtime"

    def test_pep621_optional_dependencies(self):
        text = '[project.optional-dependencies]\ntest = ["pytest>=7.0"]'
        deps, warns = PyProjectParser().parse(text, "pyproject.toml")
        assert len(deps) == 1
        assert deps[0].name == "pytest"
        assert deps[0].category == "optional"

    def test_poetry_dependencies(self):
        text = '[tool.poetry.dependencies]\nfastapi = "^0.104.0"\npython = "^3.11"'
        deps, warns = PyProjectParser().parse(text, "pyproject.toml")
        assert len(deps) == 1
        assert deps[0].name == "fastapi"
        assert deps[0].version == "^0.104.0"
        assert deps[0].category == "runtime"

    def test_poetry_dev_dependencies(self):
        text = '[tool.poetry.dev-dependencies]\npytest = "^7.0"'
        deps, warns = PyProjectParser().parse(text, "pyproject.toml")
        assert len(deps) == 1
        assert deps[0].name == "pytest"
        assert deps[0].category == "development"

    def test_poetry_group_dev(self):
        text = '[tool.poetry.group.dev.dependencies]\npytest = "^7.0"'
        deps, warns = PyProjectParser().parse(text, "pyproject.toml")
        assert len(deps) == 1
        assert deps[0].name == "pytest"
        assert deps[0].category == "development"

    def test_poetry_group_other(self):
        text = '[tool.poetry.group.docs.dependencies]\nsphinx = "^6.0"'
        deps, warns = PyProjectParser().parse(text, "pyproject.toml")
        assert len(deps) == 1
        assert deps[0].category == "optional"

    def test_corrupt_toml(self):
        deps, warns = PyProjectParser().parse("[[[invalid", "pyproject.toml")
        assert deps == []
        assert len(warns) == 1

    def test_empty(self):
        deps, warns = PyProjectParser().parse("", "pyproject.toml")
        assert deps == []
        assert warns == []


# ─── PomParser Tests ────────────────────────────────────────────────────


class TestPomParser:

    POM = """<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
      <version>3.0.0</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>"""

    def test_dependencies(self):
        deps, warns = PomParser().parse(self.POM, "pom.xml")
        assert len(deps) == 2
        names = {d.name for d in deps}
        assert names == {"junit:junit", "org.springframework.boot:spring-boot-starter-web"}
        versions = {(d.name, d.version) for d in deps}
        assert ("junit:junit", "4.13.2") in versions
        assert ("org.springframework.boot:spring-boot-starter-web", "3.0.0") in versions
        cats = {d.name: d.category for d in deps}
        assert cats["junit:junit"] == "development"
        assert cats["org.springframework.boot:spring-boot-starter-web"] == "runtime"

    def test_no_version(self):
        pom = """<project><dependencies><dependency>
      <groupId>com.example</groupId><artifactId>lib</artifactId>
    </dependency></dependencies></project>"""
        deps, warns = PomParser().parse(pom, "pom.xml")
        assert len(deps) == 1
        assert deps[0].version is None

    def test_corrupt_xml(self):
        deps, warns = PomParser().parse("not xml", "pom.xml")
        assert deps == []
        assert len(warns) == 1

    def test_empty(self):
        deps, warns = PomParser().parse("<project></project>", "pom.xml")
        assert deps == []

    def test_optional_dependency(self):
        pom = """<project><dependencies><dependency>
      <groupId>com.example</groupId><artifactId>opt</artifactId>
      <optional>true</optional>
    </dependency></dependencies></project>"""
        deps, warns = PomParser().parse(pom, "pom.xml")
        assert len(deps) == 1
        assert deps[0].category == "optional"

    def test_scope_mapping(self):
        pom = """<project><dependencies>
    <dependency><groupId>a</groupId><artifactId>b</artifactId><scope>provided</scope></dependency>
    <dependency><groupId>c</groupId><artifactId>d</artifactId><scope>runtime</scope></dependency>
    <dependency><groupId>e</groupId><artifactId>f</artifactId><scope>system</scope></dependency>
    </dependencies></project>"""
        deps, warns = PomParser().parse(pom, "pom.xml")
        cats = {d.name: d.category for d in deps}
        assert cats["a:b"] == "runtime"
        assert cats["c:d"] == "runtime"
        assert cats["e:f"] == "system"


# ─── GradleParser Tests ─────────────────────────────────────────────────


class TestGradleParser:

    def test_implementation_with_parens(self):
        text = '''dependencies {
    implementation("org.springframework.boot:spring-boot-starter:3.0.0")
}'''
        deps, warns = GradleParser().parse(text, "build.gradle")
        assert len(deps) == 1
        assert deps[0].name == "org.springframework.boot:spring-boot-starter"
        assert deps[0].version == "3.0.0"
        assert deps[0].ecosystem == "gradle"
        assert deps[0].category == "runtime"

    def test_implementation_no_parens(self):
        text = "implementation 'com.example:lib:1.0'"
        deps, warns = GradleParser().parse(text, "build.gradle")
        assert len(deps) == 1
        assert deps[0].name == "com.example:lib"
        assert deps[0].version == "1.0"

    def test_test_implementation(self):
        text = "testImplementation 'junit:junit:4.13'"
        deps, warns = GradleParser().parse(text, "build.gradle")
        assert len(deps) == 1
        assert deps[0].category == "development"

    def test_api_and_compile_only(self):
        text = "api 'com.google.guava:guava:31.0'\ncompileOnly 'org.projectlombok:lombok:1.18.0'"
        deps, warns = GradleParser().parse(text, "build.gradle")
        assert len(deps) == 2
        cats = {d.name: d.category for d in deps}
        assert cats["com.google.guava:guava"] == "runtime"
        assert cats["org.projectlombok:lombok"] == "build"

    def test_no_version(self):
        text = "implementation 'com.example:lib'"
        deps, warns = GradleParser().parse(text, "build.gradle")
        assert len(deps) == 1
        assert deps[0].version is None

    def test_no_matches(self):
        text = "println 'hello'"
        deps, warns = GradleParser().parse(text, "build.gradle")
        assert deps == []
        assert len(warns) == 1


# ─── CargoParser Tests ──────────────────────────────────────────────────


class TestCargoParser:

    def test_dependencies(self):
        text = '[dependencies]\nserde = "1.0"\nactix-web = "4.0"'
        deps, warns = CargoParser().parse(text, "Cargo.toml")
        assert len(deps) == 2
        names = {d.name for d in deps}
        assert names == {"serde", "actix-web"}
        assert all(d.ecosystem == "cargo" for d in deps)
        assert all(d.category == "runtime" for d in deps)

    def test_dev_dependencies(self):
        text = '[dev-dependencies]\ncriterion = "0.5"'
        deps, warns = CargoParser().parse(text, "Cargo.toml")
        assert len(deps) == 1
        assert deps[0].category == "development"

    def test_build_dependencies(self):
        text = '[build-dependencies]\ncc = "1.0"'
        deps, warns = CargoParser().parse(text, "Cargo.toml")
        assert len(deps) == 1
        assert deps[0].category == "build"

    def test_table_format(self):
        text = '[dependencies]\nserde = { version = "1.0", features = ["derive"] }'
        deps, warns = CargoParser().parse(text, "Cargo.toml")
        assert len(deps) == 1
        assert deps[0].version == "1.0"

    def test_git_dependency(self):
        text = '[dependencies]\nmycrate = { git = "https://github.com/user/mycrate" }'
        deps, warns = CargoParser().parse(text, "Cargo.toml")
        assert len(deps) == 1
        assert deps[0].version is None

    def test_corrupt_toml(self):
        deps, warns = CargoParser().parse("[[[invalid", "Cargo.toml")
        assert deps == []
        assert len(warns) == 1

    def test_empty(self):
        deps, warns = CargoParser().parse("", "Cargo.toml")
        assert deps == []
        assert warns == []


# ─── ComposerParser Tests ────────────────────────────────────────────────


class TestComposerParser:

    def test_require(self):
        text = '{"require": {"laravel/framework": "^10.0", "php": "^8.1"}}'
        deps, warns = ComposerParser().parse(text, "composer.json")
        assert len(deps) == 2
        assert deps[0].ecosystem == "packagist"
        assert deps[0].category == "runtime"

    def test_require_dev(self):
        text = '{"require-dev": {"phpunit/phpunit": "^9.0"}}'
        deps, warns = ComposerParser().parse(text, "composer.json")
        assert len(deps) == 1
        assert deps[0].category == "development"

    def test_corrupt_json(self):
        deps, warns = ComposerParser().parse("not json", "composer.json")
        assert deps == []
        assert len(warns) == 1

    def test_empty(self):
        deps, warns = ComposerParser().parse("{}", "composer.json")
        assert deps == []
        assert warns == []


# ─── GemfileParser Tests ─────────────────────────────────────────────────


class TestGemfileParser:

    def test_gem_with_version(self):
        text = "gem 'rails', '~> 7.0'"
        deps, warns = GemfileParser().parse(text, "Gemfile")
        assert len(deps) == 1
        assert deps[0].name == "rails"
        assert deps[0].version == "~> 7.0"
        assert deps[0].ecosystem == "rubygems"
        assert deps[0].category == "runtime"

    def test_gem_no_version(self):
        text = 'gem "pg"'
        deps, warns = GemfileParser().parse(text, "Gemfile")
        assert len(deps) == 1
        assert deps[0].version is None

    def test_double_quotes(self):
        text = 'gem "rails", "7.0"'
        deps, warns = GemfileParser().parse(text, "Gemfile")
        assert len(deps) == 1
        assert deps[0].version == "7.0"

    def test_comments(self):
        text = "# this is a comment\ngem 'rails'\n"
        deps, warns = GemfileParser().parse(text, "Gemfile")
        assert len(deps) == 1
        assert warns == []

    def test_multiple(self):
        text = "gem 'rails'\ngem 'pg'\ngem 'puma'"
        deps, warns = GemfileParser().parse(text, "Gemfile")
        assert len(deps) == 3

    def test_no_gems(self):
        text = "# empty file"
        deps, warns = GemfileParser().parse(text, "Gemfile")
        assert deps == []
        assert warns == []


# ─── CsProjParser Tests ─────────────────────────────────────────────────


class TestCsProjParser:

    CSPROJ = """<Project Sdk="Microsoft.NET.Sdk.Web">
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Mvc" Version="6.0.0" />
    <PackageReference Include="Newtonsoft.Json" Version="13.0.0" />
  </ItemGroup>
</Project>"""

    def test_package_references(self):
        deps, warns = CsProjParser().parse(self.CSPROJ, "api.csproj")
        assert len(deps) == 2
        assert deps[0].name == "Microsoft.AspNetCore.Mvc"
        assert deps[0].version == "6.0.0"
        assert deps[0].ecosystem == "nuget"
        assert deps[0].category == "runtime"

    def test_no_version(self):
        csproj = '<Project><ItemGroup><PackageReference Include="MyPackage" /></ItemGroup></Project>'
        deps, warns = CsProjParser().parse(csproj, "test.csproj")
        assert len(deps) == 1
        assert deps[0].version is None

    def test_corrupt_xml(self):
        deps, warns = CsProjParser().parse("not xml", "test.csproj")
        assert deps == []
        assert len(warns) == 1

    def test_empty(self):
        deps, warns = CsProjParser().parse("<Project></Project>", "test.csproj")
        assert deps == []
        assert warns == []


# ─── Parser Registry Tests ──────────────────────────────────────────────


class TestParserRegistry:

    def test_exact_match(self):
        parsers = _resolve_parsers("package.json")
        assert PackageJsonParser in parsers

    def test_csproj_wildcard(self):
        parsers = _resolve_parsers("api.csproj")
        assert CsProjParser in parsers

    def test_csproj_another(self):
        parsers = _resolve_parsers("test.csproj")
        assert CsProjParser in parsers

    def test_unknown(self):
        parsers = _resolve_parsers("main.py")
        assert parsers == []

    def test_all_known(self):
        known = ["package.json", "requirements.txt", "pyproject.toml", "pom.xml",
                  "build.gradle", "build.gradle.kts", "composer.json", "Cargo.toml", "Gemfile"]
        for name in known:
            parsers = _resolve_parsers(name)
            assert len(parsers) >= 1, f"{name} has no parsers"


# ─── _merge_deduplicate Tests ──────────────────────────────────────────


class TestMergeDeduplicate:

    def test_no_duplicates(self):
        raw = [
            _RawDependency("react", "^18.0.0", "npm", "runtime", "package.json"),
            _RawDependency("express", "^4.18.0", "npm", "runtime", "package.json"),
        ]
        merged, warns = _merge_deduplicate(raw)
        assert len(merged) == 2
        assert warns == []

    def test_same_name_same_category_merged(self):
        raw = [
            _RawDependency("react", "^18.0.0", "npm", "runtime", "package.json"),
            _RawDependency("react", "^18.0.0", "npm", "runtime", "package-lock.json"),
        ]
        merged, warns = _merge_deduplicate(raw)
        assert len(merged) == 1
        assert merged[0].source_files == ("package-lock.json", "package.json")

    def test_same_name_different_category_separate(self):
        raw = [
            _RawDependency("jest", "^29.0.0", "npm", "runtime", "package.json"),
            _RawDependency("jest", "^29.0.0", "npm", "development", "package.json"),
        ]
        merged, warns = _merge_deduplicate(raw)
        assert len(merged) == 2

    def test_same_name_different_ecosystem_separate(self):
        raw = [
            _RawDependency("chalk", "5.0.0", "npm", "runtime", "package.json"),
            _RawDependency("chalk", "5.0.0", "pip", "runtime", "requirements.txt"),
        ]
        merged, warns = _merge_deduplicate(raw)
        assert len(merged) == 2

    def test_version_conflict_warning(self):
        raw = [
            _RawDependency("react", "^18.0.0", "npm", "runtime", "package.json"),
            _RawDependency("react", "^19.0.0", "npm", "runtime", "other.json"),
        ]
        merged, warns = _merge_deduplicate(raw)
        assert len(merged) == 1
        assert len(warns) == 1
        assert "Version conflict" in warns[0]

    def test_deterministic_ordering(self):
        raw = [
            _RawDependency("z", "1.0", "npm", "runtime", "p.json"),
            _RawDependency("a", "1.0", "npm", "runtime", "p.json"),
            _RawDependency("m", "1.0", "npm", "runtime", "p.json"),
        ]
        merged, warns = _merge_deduplicate(raw)
        names = [d.name for d in merged]
        assert names == ["a", "m", "z"]

    def test_source_files_deterministic(self):
        raw = [
            _RawDependency("react", "^18.0.0", "npm", "runtime", "z.json"),
            _RawDependency("react", "^18.0.0", "npm", "runtime", "a.json"),
        ]
        merged, warns = _merge_deduplicate(raw)
        assert merged[0].source_files == ("a.json", "z.json")


# ─── DependencyDetector Integration Tests ──────────────────────────────


class TestDependencyDetector:

    def test_detector_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            result = DependencyDetector().detect(ctx)
        assert result.detector_name == "DependencyDetector"

    def test_empty_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert result.dependencies == ()

    def test_npm_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({"dependencies": {"react": "^18.0.0", "express": "^4.18.0"}}),
            })
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert len(result.dependencies) == 2
        names = {d.name for d in result.dependencies}
        assert names == {"react", "express"}
        for d in result.dependencies:
            assert d.ecosystem == "npm"
            assert d.category == "runtime"

    def test_multiple_ecosystems(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({"dependencies": {"react": "^18.0.0"}}),
                "requirements.txt": "flask>=2.0\nrequests==2.31.0",
            })
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert len(result.dependencies) == 3

    def test_pyproject_pep621(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "pyproject.toml": '[project]\ndependencies = ["fastapi>=0.100.0"]',
            })
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert len(result.dependencies) == 1
        assert result.dependencies[0].name == "fastapi"
        assert result.dependencies[0].ecosystem == "python"

    def test_maven_pom(self):
        pom = """<project><dependencies>
    <dependency><groupId>org.junit</groupId><artifactId>junit5</artifactId><version>5.9.0</version><scope>test</scope></dependency>
</dependencies></project>"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"pom.xml": pom})
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert len(result.dependencies) == 1
        assert result.dependencies[0].ecosystem == "maven"
        assert result.dependencies[0].category == "development"

    def test_gradle(self):
        text = "implementation 'com.example:lib:1.0'\ntestImplementation 'junit:junit:4.13'"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"build.gradle": text})
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert len(result.dependencies) == 2
        cats = {d.name: d.category for d in result.dependencies}
        assert cats["com.example:lib"] == "runtime"
        assert cats["junit:junit"] == "development"

    def test_cargo(self):
        text = '[dependencies]\nserde = "1.0"\n[dev-dependencies]\ncriterion = "0.5"'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"Cargo.toml": text})
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert len(result.dependencies) == 2
        cats = {d.name: d.category for d in result.dependencies}
        assert cats["serde"] == "runtime"
        assert cats["criterion"] == "development"

    def test_composer(self):
        text = json.dumps({"require": {"laravel/framework": "^10.0"}, "require-dev": {"phpunit/phpunit": "^9.0"}})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"composer.json": text})
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert len(result.dependencies) == 2
        cats = {d.name: d.category for d in result.dependencies}
        assert cats["laravel/framework"] == "runtime"
        assert cats["phpunit/phpunit"] == "development"

    def test_gemfile(self):
        text = "gem 'rails', '~> 7.0'\ngem 'pg'"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"Gemfile": text})
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert len(result.dependencies) == 2
        assert all(d.ecosystem == "rubygems" for d in result.dependencies)

    def test_csproj(self):
        csproj = """<Project><ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.0" />
</ItemGroup></Project>"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"app.csproj": csproj})
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.error is None
        assert len(result.dependencies) == 1
        assert result.dependencies[0].ecosystem == "nuget"
        assert result.dependencies[0].category == "runtime"

    def test_deterministic_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({"dependencies": {"z": "1.0", "a": "2.0", "m": "3.0"}}),
                "requirements.txt": "flask>=2.0\nbottle>=0.12",
            })
            ctx = _discover(root)
            r1 = DependencyDetector().detect(ctx)
            r2 = DependencyDetector().detect(ctx)
        assert r1.dependencies == r2.dependencies

    def test_version_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({"dependencies": {"react": "^18.2.0"}}),
            })
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.dependencies[0].version == "^18.2.0"

    def test_missing_source_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {})
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.dependencies == ()

    def test_corrupted_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"package.json": "corrupt json"})
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert result.dependencies == ()

    def test_duplicate_merged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": json.dumps({"dependencies": {"react": "^18.0.0"}}),
            })
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert len(result.dependencies) == 1
        assert result.dependencies[0].name == "react"

    def test_partial_parse_continues(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": "corrupt",
                "requirements.txt": "flask>=2.0",
            })
            ctx = _discover(root)
            result = DependencyDetector().detect(ctx)
        assert len(result.dependencies) == 1
        assert result.dependencies[0].name == "flask"

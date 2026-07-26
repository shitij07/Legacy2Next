import tempfile
from pathlib import Path

import pytest

from app.modules.analysis.base import BaseDetector
from app.modules.analysis.discovery import DiscoveryEngine
from app.modules.analysis.language_detector import LanguageDetector
from app.modules.analysis.types import (
    AnalysisResults,
    DetectedDependency,
    DetectedFile,
    DetectedMetric,
    DetectedTechnology,
    DetectorResult,
    DiscoveryContext,
    FileGraph,
)
from app.modules.analysis.utils import classify_extension, is_known_extension


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


# ─── DetectorResult Tests ────────────────────────────────────────────────


class TestDetectorResult:

    def test_immutable(self):
        r = DetectorResult(detector_name="Test")
        with pytest.raises((AttributeError, TypeError)):
            r.error = "changed"  # type: ignore

    def test_empty_result(self):
        r = DetectorResult(detector_name="Test")
        assert r.detector_name == "Test"
        assert r.technologies == ()
        assert r.files == ()
        assert r.dependencies == ()
        assert r.metrics == ()
        assert r.error is None

    def test_error_result(self):
        r = DetectorResult(detector_name="Test", error="Something broke")
        assert r.error == "Something broke"

    def test_with_technologies(self):
        t = DetectedTechnology(name="Python", category="language", evidence="5 files (100%)")
        r = DetectorResult(detector_name="Test", technologies=(t,))
        assert len(r.technologies) == 1
        assert r.technologies[0].name == "Python"

    def test_with_multiple_fields(self):
        t = DetectedTechnology(name="Python", category="language")
        m = DetectedMetric(key="total_files", value=10)
        r = DetectorResult(detector_name="Test", technologies=(t,), metrics=(m,))
        assert len(r.technologies) == 1
        assert len(r.metrics) == 1


# ─── DetectedTechnology Tests ────────────────────────────────────────────


class TestDetectedTechnology:

    def test_defaults(self):
        t = DetectedTechnology(name="Python", category="language")
        assert t.name == "Python"
        assert t.category == "language"
        assert t.evidence is None
        assert t.confidence == "high"

    def test_all_fields(self):
        t = DetectedTechnology(
            name="React",
            category="framework",
            evidence="package.json",
            confidence="medium",
        )
        assert t.evidence == "package.json"
        assert t.confidence == "medium"

    def test_immutable(self):
        t = DetectedTechnology(name="Go", category="language")
        with pytest.raises((AttributeError, TypeError)):
            t.name = "Rust"  # type: ignore


# ─── DetectedFile Tests ──────────────────────────────────────────────────


class TestDetectedFile:

    def test_defaults(self):
        f = DetectedFile(
            relative_path="main.py",
            file_name="main.py",
            extension=".py",
            file_size=100,
        )
        assert f.language is None

    def test_with_language(self):
        f = DetectedFile(
            relative_path="main.py",
            file_name="main.py",
            extension=".py",
            file_size=100,
            language="Python",
        )
        assert f.language == "Python"


# ─── DetectedDependency Tests ────────────────────────────────────────────


class TestDetectedDependency:

    def test_defaults(self):
        d = DetectedDependency(name="requests")
        assert d.version is None
        assert d.type == "library"
        assert d.source_file is None
        assert d.ecosystem is None

    def test_all_fields(self):
        d = DetectedDependency(
            name="express",
            version="^4.18",
            type="runtime",
            source_file="package.json",
            ecosystem="npm",
        )
        assert d.version == "^4.18"


# ─── DetectedMetric Tests ────────────────────────────────────────────────


class TestDetectedMetric:

    def test_creation(self):
        m = DetectedMetric(key="total_files", value=42)
        assert m.key == "total_files"
        assert m.value == 42

    def test_int_value(self):
        m = DetectedMetric(key="total_size", value=1048576)
        assert isinstance(m.value, int)

    def test_immutable(self):
        m = DetectedMetric(key="k", value=1)
        with pytest.raises((AttributeError, TypeError)):
            m.value = 2  # type: ignore


# ─── AnalysisResults Tests ───────────────────────────────────────────────


class TestAnalysisResults:

    def test_empty(self):
        results = AnalysisResults(results=[], start_time=0.0)
        assert results.all_technologies == []
        assert results.all_files == []
        assert results.all_dependencies == []
        assert results.all_metrics == []
        assert results.errors == []
        assert results.has_errors is False

    def test_single_result(self):
        t = DetectedTechnology(name="Python", category="language")
        r = DetectorResult(detector_name="LD", technologies=(t,))
        results = AnalysisResults(results=[r], start_time=0.0)
        assert len(results.all_technologies) == 1
        assert results.all_technologies[0].name == "Python"

    def test_multiple_results_aggregation(self):
        t1 = DetectedTechnology(name="Python", category="language")
        t2 = DetectedTechnology(name="JavaScript", category="language")
        r1 = DetectorResult(detector_name="LD", technologies=(t1,))
        r2 = DetectorResult(detector_name="LD", technologies=(t2,))
        results = AnalysisResults(results=[r1, r2], start_time=0.0)
        assert len(results.all_technologies) == 2

    def test_errors(self):
        r1 = DetectorResult(detector_name="D1", error="fail")
        r2 = DetectorResult(detector_name="D2")
        results = AnalysisResults(results=[r1, r2], start_time=0.0)
        assert results.errors == ["fail"]
        assert results.has_errors is True

    def test_no_errors(self):
        r = DetectorResult(detector_name="D1")
        results = AnalysisResults(results=[r], start_time=0.0)
        assert results.errors == []
        assert results.has_errors is False

    def test_mixed_results(self):
        t = DetectedTechnology(name="Go", category="language")
        f = DetectedFile(relative_path="main.go", file_name="main.go", extension=".go", file_size=50)
        d = DetectedDependency(name="gorilla/mux")
        m = DetectedMetric(key="files", value=1)
        r = DetectorResult(
            detector_name="Test",
            technologies=(t,),
            files=(f,),
            dependencies=(d,),
            metrics=(m,),
        )
        results = AnalysisResults(results=[r], start_time=0.0)
        assert len(results.all_technologies) == 1
        assert len(results.all_files) == 1
        assert len(results.all_dependencies) == 1
        assert len(results.all_metrics) == 1

    def test_end_time(self):
        results = AnalysisResults(results=[], start_time=1.0, end_time=2.0)
        assert results.end_time == 2.0


# ─── Utility Tests ───────────────────────────────────────────────────────


class TestClassifyExtension:

    def test_known_extensions(self):
        cases = [
            (".py", "Python"),
            (".js", "JavaScript"),
            (".ts", "TypeScript"),
            (".java", "Java"),
            (".go", "Go"),
            (".rs", "Rust"),
            (".rb", "Ruby"),
            (".php", "PHP"),
            (".swift", "Swift"),
            (".kt", "Kotlin"),
            (".cs", "C#"),
            (".cpp", "C++"),
            (".c", "C"),
            (".html", "HTML"),
            (".css", "CSS"),
            (".json", "JSON"),
            (".yaml", "YAML"),
            (".md", "Markdown"),
            (".sql", "SQL"),
            (".sh", "Shell"),
            (".vue", "Vue"),
            (".tsx", "TypeScript"),
            (".dart", "Dart"),
        ]
        for ext, expected in cases:
            assert classify_extension(ext) == expected, f"{ext} → {expected}"

    def test_case_insensitive(self):
        assert classify_extension(".PY") == "Python"
        assert classify_extension(".Py") == "Python"
        assert classify_extension(".JSON") == "JSON"

    def test_unknown_extension(self):
        assert classify_extension(".xyz") is None
        assert classify_extension(".abc123") is None

    def test_no_extension(self):
        assert classify_extension("") is None

    def test_dotfile(self):
        assert classify_extension(".gitignore") is not None

    def test_compound_extension(self):
        assert classify_extension(".tar.gz") is None


class TestIsKnownExtension:

    def test_known(self):
        assert is_known_extension(".py") is True
        assert is_known_extension(".js") is True

    def test_unknown(self):
        assert is_known_extension(".xyz") is False

    def test_empty(self):
        assert is_known_extension("") is False


# ─── BaseDetector Tests ──────────────────────────────────────────────────


class TestBaseDetector:

    def test_detector_name(self):
        class MyDetector(BaseDetector):
            def detect(self, context: DiscoveryContext) -> DetectorResult:
                return DetectorResult(detector_name=self.detector_name)

        d = MyDetector()
        assert d.detector_name == "MyDetector"

    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseDetector()  # type: ignore

    def test_logger(self):
        d = _create_concrete_detector()
        assert d._logger.name.endswith("ConcreteDetector")

    def test_read_text_no_root(self):
        d = _create_concrete_detector()
        assert d.read_text("nonexistent.py") is None

    def test_read_text_with_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "hello.py").write_text("print('hi')", encoding="utf-8")
            d = _create_concrete_detector()
            d._context_root = root
            content = d.read_text("hello.py")
            assert content == "print('hi')"

    def test_read_text_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = _create_concrete_detector()
            d._context_root = Path(tmp)
            assert d.read_text("nonexistent.py") is None

    def test_read_text_unreadable(self):
        class ReadOnlyDetector(BaseDetector):
            def detect(self, context: DiscoveryContext) -> DetectorResult:
                return DetectorResult(detector_name=self.detector_name)

        d = ReadOnlyDetector()
        assert d.read_text("/") is None  # root dir isn't text


def _create_concrete_detector() -> BaseDetector:
    class ConcreteDetector(BaseDetector):
        def detect(self, context: DiscoveryContext) -> DetectorResult:
            return DetectorResult(detector_name=self.detector_name)

    return ConcreteDetector()


# ─── LanguageDetector Tests ──────────────────────────────────────────────


class TestLanguageDetector:

    def test_empty_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            result = LanguageDetector().detect(ctx)
        assert result.detector_name == "LanguageDetector"
        assert result.technologies == ()
        assert result.files == ()
        assert result.error is None

    def test_single_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "main.py": "",
                "utils.py": "",
                "test.py": "",
            })
            ctx = _discover(root)
            result = LanguageDetector().detect(ctx)
        assert result.error is None
        assert len(result.technologies) == 1
        assert result.technologies[0].name == "Python"
        assert result.technologies[0].category == "language"
        assert "3 files (100%)" in result.technologies[0].evidence
        assert len(result.files) == 3
        for f in result.files:
            assert f.language == "Python"

    def test_mixed_languages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "app.py": "",
                "main.js": "",
                "styles.css": "",
                "index.html": "",
            })
            ctx = _discover(root)
            result = LanguageDetector().detect(ctx)
        assert result.error is None
        names = {t.name for t in result.technologies}
        assert names == {"Python", "JavaScript", "CSS", "HTML"}
        assert len(result.files) == 4

    def test_unknown_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "file.xyz": "",
                "data.abc123": "",
                "readme.md": "",
            })
            ctx = _discover(root)
            result = LanguageDetector().detect(ctx)
        assert result.error is None
        tech_names = {t.name for t in result.technologies}
        assert "Markdown" in tech_names
        assert "Unknown" in tech_names
        unknown = [t for t in result.technologies if t.name == "Unknown"]
        assert len(unknown) == 1
        assert unknown[0].confidence == "low"

    def test_deterministic_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "z.py": "",
                "a.py": "",
                "m.js": "",
            })
            ctx = _discover(root)
            r1 = LanguageDetector().detect(ctx)
            r2 = LanguageDetector().detect(ctx)
        assert r1.technologies == r2.technologies
        assert r1.files == r2.files

    def test_duplicate_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "a.py": "",
                "b.py": "",
                "c.py": "",
            })
            ctx = _discover(root)
            result = LanguageDetector().detect(ctx)
        assert len(result.technologies) == 1
        assert result.technologies[0].name == "Python"
        assert result.technologies[0].evidence == "3 files (100%)"

    def test_files_without_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "Dockerfile": "",
                "Makefile": "",
                "app.py": "",
            })
            ctx = _discover(root)
            result = LanguageDetector().detect(ctx)
        assert result.error is None
        python = [t for t in result.technologies if t.name == "Python"]
        unknown = [t for t in result.technologies if t.name == "Unknown"]
        assert len(python) == 1
        assert len(unknown) == 1
        assert unknown[0].confidence == "low"
        noext_files = [f for f in result.files if f.language is None]
        assert len(noext_files) == 2

    def test_large_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {}
            for i in range(100):
                files[f"src/a{i}.py"] = ""
                files[f"src/b{i}.js"] = ""
            _create_project(root, files)
            ctx = _discover(root)
            result = LanguageDetector().detect(ctx)
        assert result.error is None
        assert len(result.technologies) == 2
        py = [t for t in result.technologies if t.name == "Python"][0]
        js = [t for t in result.technologies if t.name == "JavaScript"][0]
        assert py.evidence == "100 files (50%)"
        assert js.evidence == "100 files (50%)"

    def test_detected_file_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"hello_world.py": "print('hello')"})
            ctx = _discover(root)
            result = LanguageDetector().detect(ctx)
        f = result.files[0]
        assert f.relative_path == "hello_world.py"
        assert f.file_name == "hello_world.py"
        assert f.extension == ".py"
        assert f.file_size > 0
        assert f.language == "Python"

    def test_detector_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _discover(Path(tmp))
            result = LanguageDetector().detect(ctx)
        assert result.detector_name == "LanguageDetector"

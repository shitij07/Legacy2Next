import tempfile
from pathlib import Path

import pytest

from app.modules.analysis.discovery import DiscoveryEngine, DiscoveryException
from app.modules.analysis.ignore_rules import IgnorePattern, IgnoreRules
from app.modules.analysis.types import DirectoryNode, FileNode


def _create_project(root: Path, structure: dict[str, str | None]) -> None:
    for path, content in structure.items():
        full = root / path
        if content is None:
            full.mkdir(parents=True, exist_ok=True)
        else:
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")


class TestDiscoveryEngine:

    def test_empty_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        assert ctx.stats.total_files == 0
        assert ctx.stats.total_directories == 1
        assert ctx.stats.ignored_entries == 0
        assert ctx.upload_id == 1
        assert ctx.project_id == 1

    def test_nested_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "src/__init__.py": "",
                "src/main.py": "print('hello')",
                "src/utils/helper.py": "# helper",
                "README.md": "# Project",
                "data/config.json": '{"key": "value"}',
            })
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        assert ctx.stats.total_files == 5
        assert ctx.stats.total_directories == 4
        assert ctx.stats.ignored_entries == 0

        # FileGraph assertions
        fg = ctx.file_graph
        assert len(fg.files) == 5
        assert len(fg.directories) == 4

        assert fg.get_node(".") is not None
        assert isinstance(fg.get_node("."), DirectoryNode)

        assert fg.get_node("src") is not None
        assert fg.get_node("src/main.py") is not None
        assert fg.get_node("data") is not None

        # Tree assertion
        children_root = fg.get_children(".")
        assert "README.md" in children_root
        assert "src" in children_root
        assert "data" in children_root

        children_src = fg.get_children("src")
        assert "src/__init__.py" in children_src
        assert "src/main.py" in children_src
        assert "src/utils" in children_src

    def test_ignored_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "src/app.py": "app",
                "node_modules/express/index.js": "module",
                ".git/config": "[core]",
                "dist/bundle.js": "bundled",
            })
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        assert ctx.stats.total_files == 1
        assert ctx.stats.total_directories == 2
        assert ctx.stats.ignored_entries == 3

        assert ctx.file_graph.get_node("src/app.py") is not None
        assert ctx.file_graph.get_node("node_modules") is None
        assert ctx.file_graph.get_node("dist") is None
        assert ctx.file_graph.get_node(".git") is None

    def test_ignored_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "main.py": "code",
                ".DS_Store": "",
                "build.pyc": "compiled",
                "Thumbs.db": "",
            })
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        assert ctx.stats.total_files == 1
        assert ctx.stats.ignored_entries == 3
        assert ctx.file_graph.get_node("main.py") is not None

    def test_mixed_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "a.py": "",
                "b.js": "",
                "c.java": "",
                "d.txt": "",
                "e.md": "",
            })
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        assert ctx.stats.total_files == 5
        extensions = {f.extension for f in ctx.file_graph.files}
        assert extensions == {".py", ".js", ".java", ".txt", ".md"}

    def test_invalid_root_path(self):
        with pytest.raises(DiscoveryException, match="does not exist"):
            DiscoveryEngine().discover(
                root_path=Path("/nonexistent/path"),
                upload_id=1,
                project_id=1,
            )

    def test_root_path_is_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "file.txt"
            root.write_text("content", encoding="utf-8")
            with pytest.raises(DiscoveryException, match="not a directory"):
                DiscoveryEngine().discover(
                    root_path=root,
                    upload_id=1,
                    project_id=1,
                )

    def test_file_graph_by_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "dir/a.py": "",
                "dir/b.py": "",
            })
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        fg = ctx.file_graph
        assert isinstance(fg.get_node("dir/a.py"), FileNode)
        assert isinstance(fg.get_node("dir"), DirectoryNode)
        assert isinstance(fg.get_node("."), DirectoryNode)
        assert fg.get_node("nonexistent") is None

    def test_discovery_stats_correctness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "a.py": "",
                "dir/b.py": "",
                "node_modules/pkg/c.py": "",
            })
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        assert ctx.stats.total_files == 2
        assert ctx.stats.total_directories == 2
        assert ctx.stats.ignored_entries == 1
        assert ctx.stats.duration_ms >= 0

    def test_file_node_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"hello.py": "print('hello')"})
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        node = ctx.file_graph.files[0]
        assert node.file_name == "hello.py"
        assert node.extension == ".py"
        assert node.relative_path == "hello.py"
        assert node.file_size > 0
        assert node.is_directory is False

    def test_directory_node_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"src/lib/a.py": ""})
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        src = ctx.file_graph.get_node("src")
        assert src is not None
        assert isinstance(src, DirectoryNode)
        assert src.directory_name == "src"
        assert src.relative_path == "src"
        assert src.is_directory is True

        lib = ctx.file_graph.get_node("src/lib")
        assert lib is not None
        assert isinstance(lib, DirectoryNode)
        assert lib.directory_name == "lib"
        assert lib.relative_path == "src/lib"

    def test_custom_ignore_rules(self):
        rules = IgnoreRules([IgnorePattern("*.log", match_type="glob")])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {"app.py": "", "error.log": "log", "access.log": "log"})
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
                ignore_rules=rules,
            )
        assert ctx.stats.total_files == 1
        assert ctx.stats.ignored_entries == 2


    def test_deterministic_ordering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "z.py": "",
                "a.py": "",
                "m.py": "",
                "nested/b.py": "",
                "nested/a.py": "",
            })
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        paths = [f.relative_path for f in ctx.file_graph.files]
        assert paths == ["a.py", "m.py", "z.py", "nested/a.py", "nested/b.py"]

    def test_find_files_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_project(root, {
                "package.json": '{"name": "root"}',
                "src/package.json": '{"name": "lib"}',
                "README.md": "# Project",
            })
            ctx = DiscoveryEngine().discover(
                root_path=root,
                upload_id=1,
                project_id=1,
            )
        matches = ctx.file_graph.find_files_by_name("package.json")
        assert len(matches) == 2
        assert all(f.file_name == "package.json" for f in matches)

        no_matches = ctx.file_graph.find_files_by_name("nonexistent.txt")
        assert no_matches == []


class TestIgnoreRules:

    def test_default_rules_exist(self):
        rules = IgnoreRules.defaults()
        assert len(rules.patterns) > 0

    def test_should_ignore_exact_directory(self):
        rules = IgnoreRules([IgnorePattern("node_modules")])
        assert rules.should_ignore("node_modules", is_dir=True) is True
        assert rules.should_ignore("src/node_modules", is_dir=True) is True

    def test_should_ignore_glob(self):
        rules = IgnoreRules([IgnorePattern("*.pyc", match_type="glob")])
        assert rules.should_ignore("main.pyc", is_dir=False) is True
        assert rules.should_ignore("src/util.pyc", is_dir=False) is True
        assert rules.should_ignore("main.py", is_dir=False) is False

    def test_should_ignore_prefix(self):
        rules = IgnoreRules([IgnorePattern("build/", match_type="prefix")])
        assert rules.should_ignore("build/out.o", is_dir=False) is True
        assert rules.should_ignore("build/debug/out.o", is_dir=False) is True
        assert rules.should_ignore("src/main.c", is_dir=False) is False

    def test_should_ignore_suffix(self):
        rules = IgnoreRules([IgnorePattern(".log", match_type="suffix")])
        assert rules.should_ignore("error.log", is_dir=False) is True
        assert rules.should_ignore("src/access.log", is_dir=False) is True
        assert rules.should_ignore("logger.py", is_dir=False) is False

    def test_should_not_ignore(self):
        rules = IgnoreRules.defaults()
        assert rules.should_ignore("main.py", is_dir=False) is False
        assert rules.should_ignore("src/styles.css", is_dir=False) is False
        assert rules.should_ignore("README.md", is_dir=False) is False

    def test_empty_rules(self):
        rules = IgnoreRules()
        assert rules.should_ignore("anything", is_dir=False) is False
        assert rules.should_ignore("node_modules", is_dir=True) is False

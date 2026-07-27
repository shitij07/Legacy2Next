from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.modules.ai.prompt_loader import PromptLoader


def test_default_prompt_dir_exists():
    loader = PromptLoader()
    assert loader.template_dir.exists()
    assert loader.template_dir.is_dir()


def test_render_existing_template():
    loader = PromptLoader()
    content = loader.render("summary.jinja2", {
        "project_name": "Test",
        "total_files": 10,
        "total_directories": 2,
        "languages": [],
        "technologies": [],
        "dependencies": [],
        "primary_language": None,
        "total_file_size": 1000,
        "file_count_by_extension": [],
    })
    assert isinstance(content, str)
    assert "Test" in content
    assert "10" in content
    assert "2" in content


def test_render_all_templates():
    loader = PromptLoader()
    templates = [
        "summary.jinja2",
        "file_explanation.jinja2",
        "module_explanation.jinja2",
        "architecture.jinja2",
        "technical_debt.jinja2",
        "modernization.jinja2",
    ]
    dummy_context = {
        "project_name": "Test",
        "total_files": 1,
        "total_directories": 0,
        "languages": [{"name": "Python", "count": 1}],
        "technologies": [{"name": "FastAPI", "category": "backend", "confidence": "high"}],
        "dependencies": [{"name": "fastapi", "version": "0.111.0", "ecosystem": "pypi"}],
        "primary_language": "Python",
        "total_file_size": 500,
        "file_count_by_extension": [(".py", 1)],
        "relative_path": "main.py",
        "file_name": "main.py",
        "extension": ".py",
        "file_size": 500,
        "lines_of_code": 50,
        "language": "Python",
        "content": "print('hello')",
        "module_path": "src/utils",
        "files": [{"file_name": "util.py", "extension": ".py", "file_size": 200, "lines_of_code": 20}],
        "subdirectories": [],
        "languages_list": ["Python"],
        "languages_str": "Python",
        "top_level_directories": ["src", "docs"],
        "total_warnings": 5,
        "detector_breakdown": [("style", 3), ("complexity", 2)],
        "warning_samples": [{"detector_name": "style", "message": "Line too long"}],
        "total_dependencies": 10,
        "total_technologies": 3,
    }
    for tpl in templates:
        content = loader.render(tpl, dummy_context)
        assert isinstance(content, str)
        assert len(content) > 10


def test_render_missing_template():
    loader = PromptLoader()
    with pytest.raises(FileNotFoundError, match="not found"):
        loader.render("nonexistent.jinja2", {})


def test_caches_compiled_templates():
    loader = PromptLoader()
    context = {
        "project_name": "Test",
        "total_files": 1,
        "total_directories": 0,
        "languages": [],
        "technologies": [],
        "dependencies": [],
        "primary_language": None,
        "total_file_size": 0,
        "file_count_by_extension": [],
    }
    result1 = loader.render("summary.jinja2", context)
    result2 = loader.render("summary.jinja2", context)
    assert result1 == result2


def test_custom_prompt_dir():
    with TemporaryDirectory() as tmpdir:
        prompt_file = Path(tmpdir) / "custom.jinja2"
        prompt_file.write_text("Hello {{ name }}!")
        loader = PromptLoader(prompt_dir=tmpdir)
        result = loader.render("custom.jinja2", {"name": "World"})
        assert result == "Hello World!"


def test_render_with_dataclass():
    from dataclasses import dataclass

    @dataclass
    class FakeContext:
        name: str = "World"

    with TemporaryDirectory() as tmpdir:
        prompt_file = Path(tmpdir) / "greet.jinja2"
        prompt_file.write_text("Hello {{ name }}!")
        loader = PromptLoader(prompt_dir=tmpdir)
        result = loader.render("greet.jinja2", FakeContext())
        assert result == "Hello World!"


def test_render_with_nested_loop():
    with TemporaryDirectory() as tmpdir:
        prompt_file = Path(tmpdir) / "list.jinja2"
        prompt_file.write_text("{% for item in items %}- {{ item }}\n{% endfor %}")
        loader = PromptLoader(prompt_dir=tmpdir)
        result = loader.render("list.jinja2", {"items": ["a", "b", "c"]})
        assert result == "- a\n- b\n- c\n"


def test_render_with_conditional():
    with TemporaryDirectory() as tmpdir:
        prompt_file = Path(tmpdir) / "cond.jinja2"
        prompt_file.write_text("{% if show %}Visible{% else %}Hidden{% endif %}")
        loader = PromptLoader(prompt_dir=tmpdir)
        assert loader.render("cond.jinja2", {"show": True}) == "Visible"
        assert loader.render("cond.jinja2", {"show": False}) == "Hidden"

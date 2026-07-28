from datetime import datetime, timezone

from app.modules.reports.service import _generate_markdown, _generate_json


def _sample_analysis():
    class Analysis:
        id = 1
        status = "COMPLETED"
        created_at = datetime(2026, 7, 28, 12, 0, 0)
        completed_at = datetime(2026, 7, 28, 12, 5, 0)
        error_detail = None

    return Analysis()


def _sample_files():
    from app.modules.analysis.schemas import AnalysisFileResponse
    return [
        AnalysisFileResponse(id=1, relative_path="src/main.py", file_name="main.py", extension=".py", file_size=1024, language="Python", lines_of_code=50),
        AnalysisFileResponse(id=2, relative_path="README.md", file_name="README.md", extension=".md", file_size=256, language="Markdown", lines_of_code=10),
    ]


def _sample_technologies():
    from app.modules.analysis.schemas import AnalysisTechnologyResponse
    return [
        AnalysisTechnologyResponse(id=1, name="Python", category="language", confidence="high"),
        AnalysisTechnologyResponse(id=2, name="FastAPI", category="framework", confidence="high"),
    ]


def _sample_dependencies():
    from app.modules.analysis.schemas import AnalysisDependencyResponse
    return [
        AnalysisDependencyResponse(id=1, name="fastapi", version="0.115.0", type="library", source_files=["requirements.txt"], ecosystem="pip"),
        AnalysisDependencyResponse(id=2, name="pytest", version="9.0.0", type="dev", source_files=["requirements.txt"], ecosystem="pip"),
    ]


def _sample_metrics():
    from app.modules.analysis.schemas import AnalysisMetricResponse
    return [
        AnalysisMetricResponse(id=1, key="project.total_files", value=2),
        AnalysisMetricResponse(id=2, key="languages.primary", value="Python"),
    ]


def _sample_warnings():
    from app.modules.analysis.schemas import AnalysisWarningResponse
    return [
        AnalysisWarningResponse(id=1, detector_name="LanguageDetector", message="No language detected for file unknown.bin", created_at=datetime(2026, 7, 28, 12, 0, 0)),
    ]


class TestMarkdownGeneration:
    def test_contains_project_information(self):
        data = {
            "analysis": _sample_analysis(),
            "files": _sample_files(),
            "technologies": _sample_technologies(),
            "dependencies": _sample_dependencies(),
            "metrics": _sample_metrics(),
            "warnings": _sample_warnings(),
        }
        result = _generate_markdown(data, {}, "test-project")
        assert "# Analysis Report: test-project" in result
        assert "**Generated:**" in result
        assert "## Project Information" in result
        assert "## Analysis Summary" in result
        assert "## Files Overview" in result
        assert "## Technology Stack" in result
        assert "## Dependencies" in result
        assert "## Metrics" in result
        assert "## Warnings" in result

    def test_contains_all_data_rows(self):
        data = {
            "analysis": _sample_analysis(),
            "files": _sample_files(),
            "technologies": _sample_technologies(),
            "dependencies": _sample_dependencies(),
            "metrics": _sample_metrics(),
            "warnings": _sample_warnings(),
        }
        result = _generate_markdown(data, {}, "test-project")
        assert "src/main.py" in result
        assert "fastapi" in result
        assert "Python" in result
        assert "FastAPI" in result
        assert "project.total_files" in result
        assert "LanguageDetector" in result

    def test_includes_ai_sections_when_present(self):
        data = {
            "analysis": _sample_analysis(),
            "files": [],
            "technologies": [],
            "dependencies": [],
            "metrics": [],
            "warnings": [],
        }
        ai_outputs = {
            "summary": "AI summary content",
            "architecture": "AI architecture content",
            "technical_debt": "AI debt content",
            "modernization": "AI modernization content",
        }
        result = _generate_markdown(data, ai_outputs, "test-project")
        assert "## AI Summary" in result
        assert "AI summary content" in result
        assert "## Architecture" in result
        assert "AI architecture content" in result
        assert "## Technical Debt" in result
        assert "AI debt content" in result
        assert "## Modernization Recommendations" in result
        assert "AI modernization content" in result

    def test_omits_ai_sections_when_absent(self):
        data = {
            "analysis": _sample_analysis(),
            "files": [],
            "technologies": [],
            "dependencies": [],
            "metrics": [],
            "warnings": [],
        }
        result = _generate_markdown(data, {}, "test-project")
        assert "## AI Summary" not in result
        assert "## Architecture" not in result
        assert "## Technical Debt" not in result
        assert "## Modernization Recommendations" not in result

    def test_empty_data_produces_valid_markdown(self):
        result = _generate_markdown({}, {}, "empty-project")
        assert result.startswith("#")
        assert "empty-project" in result
        assert "Generated" in result


class TestJsonGeneration:
    def test_contains_all_sections(self):
        data = {
            "analysis": _sample_analysis(),
            "files": _sample_files(),
            "technologies": _sample_technologies(),
            "dependencies": _sample_dependencies(),
            "metrics": _sample_metrics(),
            "warnings": _sample_warnings(),
        }
        result = _generate_json(data, {}, "test-project")
        assert '"title": "Analysis Report: test-project"' in result
        assert '"total_files": 2' in result
        assert '"total_technologies": 2' in result
        assert '"total_dependencies": 2' in result
        assert '"total_warnings": 1' in result

    def test_includes_ai_insights_when_present(self):
        data = {
            "analysis": _sample_analysis(),
            "files": [],
            "technologies": [],
            "dependencies": [],
            "metrics": [],
            "warnings": [],
        }
        ai_outputs = {"summary": "AI text"}
        result = _generate_json(data, ai_outputs, "test-project")
        assert '"ai_insights"' in result
        assert '"summary": "AI text"' in result

    def test_omits_ai_insights_when_absent(self):
        data = {
            "analysis": _sample_analysis(),
            "files": [],
            "technologies": [],
            "dependencies": [],
            "metrics": [],
            "warnings": [],
        }
        result = _generate_json(data, {}, "test-project")
        assert '"ai_insights"' not in result

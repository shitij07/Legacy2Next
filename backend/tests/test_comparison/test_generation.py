from app.modules.comparison.service import (
    _compare_technologies,
    _compare_dependencies,
    _compare_files,
    _compare_warnings,
    _compare_metrics,
    _generate_summary,
)
from app.modules.comparison.schemas import ComparisonData


class TestTechnologyComparison:
    def test_detects_added_technologies(self):
        data_a = {"technologies": [{"name": "Python", "category": "language"}]}
        data_b = {"technologies": [{"name": "Python", "category": "language"}, {"name": "React", "category": "framework"}]}
        result = _compare_technologies(data_a, data_b)
        assert len(result.added) == 1
        assert result.added[0]["name"] == "React"
        assert len(result.removed) == 0
        assert len(result.common) == 1

    def test_detects_removed_technologies(self):
        data_a = {"technologies": [{"name": "Python", "category": "language"}, {"name": "jQuery", "category": "library"}]}
        data_b = {"technologies": [{"name": "Python", "category": "language"}]}
        result = _compare_technologies(data_a, data_b)
        assert len(result.removed) == 1
        assert result.removed[0]["name"] == "jQuery"
        assert len(result.added) == 0
        assert len(result.common) == 1

    def test_handles_empty_technologies(self):
        result = _compare_technologies({}, {})
        assert len(result.added) == 0
        assert len(result.removed) == 0
        assert len(result.common) == 0

    def test_common_technologies(self):
        data_a = {"technologies": [{"name": "Python", "category": "language"}]}
        data_b = {"technologies": [{"name": "Python", "category": "language"}]}
        result = _compare_technologies(data_a, data_b)
        assert len(result.common) == 1
        assert result.common[0]["name"] == "Python"


class TestDependencyComparison:
    def test_detects_added_dependencies(self):
        data_a = {"dependencies": [{"name": "fastapi", "ecosystem": "pip", "version": "0.115.0"}]}
        data_b = {"dependencies": [{"name": "fastapi", "ecosystem": "pip", "version": "0.115.0"}, {"name": "pytest", "ecosystem": "pip", "version": "9.0.0"}]}
        result = _compare_dependencies(data_a, data_b)
        assert len(result.added) == 1
        assert result.added[0]["name"] == "pytest"

    def test_detects_removed_dependencies(self):
        data_a = {"dependencies": [{"name": "fastapi", "ecosystem": "pip", "version": "0.115.0"}, {"name": "jquery", "ecosystem": "npm", "version": "3.0.0"}]}
        data_b = {"dependencies": [{"name": "fastapi", "ecosystem": "pip", "version": "0.115.0"}]}
        result = _compare_dependencies(data_a, data_b)
        assert len(result.removed) == 1
        assert result.removed[0]["name"] == "jquery"

    def test_detects_updated_dependencies(self):
        data_a = {"dependencies": [{"name": "fastapi", "ecosystem": "pip", "version": "0.110.0"}]}
        data_b = {"dependencies": [{"name": "fastapi", "ecosystem": "pip", "version": "0.115.0"}]}
        result = _compare_dependencies(data_a, data_b)
        assert len(result.updated) == 1
        assert result.updated[0]["from"]["version"] == "0.110.0"
        assert result.updated[0]["to"]["version"] == "0.115.0"

    def test_handles_empty_dependencies(self):
        result = _compare_dependencies({}, {})
        assert len(result.added) == 0
        assert len(result.removed) == 0
        assert len(result.updated) == 0


class TestFileComparison:
    def test_detects_added_files(self):
        data_a = {"files": [{"relative_path": "src/main.py", "file_size": 1024}]}
        data_b = {"files": [{"relative_path": "src/main.py", "file_size": 1024}, {"relative_path": "src/utils.py", "file_size": 512}]}
        result = _compare_files(data_a, data_b)
        assert len(result.added) == 1
        assert result.added[0]["relative_path"] == "src/utils.py"

    def test_detects_removed_files(self):
        data_a = {"files": [{"relative_path": "src/main.py", "file_size": 1024}, {"relative_path": "old.py", "file_size": 256}]}
        data_b = {"files": [{"relative_path": "src/main.py", "file_size": 1024}]}
        result = _compare_files(data_a, data_b)
        assert len(result.removed) == 1
        assert result.removed[0]["relative_path"] == "old.py"

    def test_detects_modified_files(self):
        data_a = {"files": [{"relative_path": "src/main.py", "file_size": 1024, "lines_of_code": 50}]}
        data_b = {"files": [{"relative_path": "src/main.py", "file_size": 2048, "lines_of_code": 100}]}
        result = _compare_files(data_a, data_b)
        assert len(result.modified) == 1
        assert result.modified[0]["path"] == "src/main.py"

    def test_counts_correctly(self):
        data_a = {"files": [{"relative_path": "a.py", "file_size": 1}]}
        data_b = {"files": [{"relative_path": "a.py", "file_size": 1}, {"relative_path": "b.py", "file_size": 2}]}
        result = _compare_files(data_a, data_b)
        assert result.total_a == 1
        assert result.total_b == 2

    def test_handles_empty_files(self):
        result = _compare_files({}, {})
        assert len(result.added) == 0
        assert len(result.removed) == 0
        assert len(result.modified) == 0


class TestWarningComparison:
    def test_detects_added_warnings(self):
        data_a = {"warnings": [{"detector_name": "D1", "message": "Warn A"}]}
        data_b = {"warnings": [{"detector_name": "D1", "message": "Warn A"}, {"detector_name": "D2", "message": "Warn B"}]}
        result = _compare_warnings(data_a, data_b)
        assert len(result.added) == 1

    def test_detects_resolved_warnings(self):
        data_a = {"warnings": [{"detector_name": "D1", "message": "Warn A"}, {"detector_name": "D2", "message": "Warn B"}]}
        data_b = {"warnings": [{"detector_name": "D1", "message": "Warn A"}]}
        result = _compare_warnings(data_a, data_b)
        assert len(result.resolved) == 1

    def test_detects_persistent_warnings(self):
        data_a = {"warnings": [{"detector_name": "D1", "message": "Warn A"}]}
        data_b = {"warnings": [{"detector_name": "D1", "message": "Warn A"}]}
        result = _compare_warnings(data_a, data_b)
        assert len(result.persistent) == 1

    def test_calculates_delta(self):
        data_a = {"warnings": [{"detector_name": "D1", "message": "Warn A"}]}
        data_b = {"warnings": [{"detector_name": "D1", "message": "Warn A"}, {"detector_name": "D2", "message": "Warn B"}]}
        result = _compare_warnings(data_a, data_b)
        assert result.delta == 1  # 1 added - 0 resolved

    def test_negative_delta(self):
        data_a = {"warnings": [{"detector_name": "D1", "message": "Warn A"}, {"detector_name": "D2", "message": "Warn B"}]}
        data_b = {"warnings": [{"detector_name": "D1", "message": "Warn A"}]}
        result = _compare_warnings(data_a, data_b)
        assert result.delta == -1  # 0 added - 1 resolved

    def test_handles_empty_warnings(self):
        result = _compare_warnings({}, {})
        assert len(result.added) == 0
        assert len(result.resolved) == 0
        assert len(result.persistent) == 0
        assert result.delta == 0


class TestMetricsComparison:
    def test_compares_integer_metrics(self):
        data_a = {"metrics": {"loc": 1000, "file_count": 20}}
        data_b = {"metrics": {"loc": 1200, "file_count": 25}}
        result = _compare_metrics(data_a, data_b)
        assert result.loc is not None
        assert result.loc.abs_diff == 200
        assert result.loc.pct_diff == 20.0
        assert result.file_count is not None
        assert result.file_count.abs_diff == 5

    def test_handles_missing_metrics(self):
        result = _compare_metrics({"metrics": {}}, {"metrics": {}})
        assert result.loc is None
        assert result.file_count is None

    def test_uses_alternative_keys(self):
        data_a = {"metrics": {"total_files": 10, "lines_of_code": 500}}
        data_b = {"metrics": {"total_files": 15, "lines_of_code": 600}}
        result = _compare_metrics(data_a, data_b)
        assert result.file_count is not None
        assert result.file_count.abs_diff == 5
        assert result.loc is not None
        assert result.loc.abs_diff == 100

    def test_negative_percentage(self):
        data_a = {"metrics": {"loc": 1000}}
        data_b = {"metrics": {"loc": 800}}
        result = _compare_metrics(data_a, data_b)
        assert result.loc is not None
        assert result.loc.abs_diff == -200
        assert result.loc.pct_diff == -20.0


class TestSummaryGeneration:
    def test_generates_summary_with_added_technologies(self):
        cd = ComparisonData(
            technologies={"added": [{"name": "React"}], "removed": [], "common": [], "version_changes": []},
            dependencies={"added": [], "removed": [], "updated": []},
            files={"added": [], "removed": [], "modified": [], "total_a": 0, "total_b": 0},
            warnings={"added": [], "resolved": [], "persistent": [], "delta": 0},
            metrics={},
        )
        summary = _generate_summary(cd)
        assert "added" in summary.lower()
        assert "react" in summary.lower()

    def test_generates_summary_for_warning_reduction(self):
        cd = ComparisonData(
            technologies={"added": [], "removed": [], "common": [], "version_changes": []},
            dependencies={"added": [], "removed": [], "updated": []},
            files={"added": [], "removed": [], "modified": [], "total_a": 0, "total_b": 0},
            warnings={"added": [], "resolved": [{"detector_name": "D1"}], "persistent": [], "delta": -1},
            metrics={},
        )
        summary = _generate_summary(cd)
        assert "resolved" in summary.lower()

    def test_no_differences(self):
        cd = ComparisonData(
            technologies={"added": [], "removed": [], "common": [], "version_changes": []},
            dependencies={"added": [], "removed": [], "updated": []},
            files={"added": [], "removed": [], "modified": [], "total_a": 0, "total_b": 0},
            warnings={"added": [], "resolved": [], "persistent": [], "delta": 0},
            metrics={},
        )
        summary = _generate_summary(cd)
        assert "no significant differences" in summary.lower()

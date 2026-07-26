from enum import StrEnum


class MetricKey(StrEnum):
    PROJECT_TOTAL_FILES = "project.total_files"
    PROJECT_TOTAL_FILE_SIZE = "project.total_file_size"
    LANGUAGE_COUNT = "languages.count"
    PRIMARY_LANGUAGE = "languages.primary"
    FRAMEWORK_COUNT = "frameworks.count"
    DEPENDENCY_COUNT = "dependencies.count"
    MANIFEST_COUNT = "manifests.count"

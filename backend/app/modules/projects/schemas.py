from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    language: str
    framework: str
    file_count: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]


class PaginatedProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    size: int
    pages: int

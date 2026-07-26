from pydantic import BaseModel
from pydantic.config import ConfigDict


class AnalysisResponse(BaseModel):
    analysis_id: int
    status: str
    error_detail: str | None = None

    model_config = ConfigDict(from_attributes=True)

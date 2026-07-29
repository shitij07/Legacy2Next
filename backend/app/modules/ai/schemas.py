from pydantic import BaseModel, Field


class ModuleExplanationRequest(BaseModel):
    module_path: str = Field(..., min_length=1, max_length=2048)


class GenerationResponse(BaseModel):
    analysis_id: int
    feature: str
    content: str
    model: str

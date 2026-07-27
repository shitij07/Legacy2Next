from pydantic import BaseModel


class ModuleExplanationRequest(BaseModel):
    module_path: str


class GenerationResponse(BaseModel):
    analysis_id: int
    feature: str
    content: str
    model: str

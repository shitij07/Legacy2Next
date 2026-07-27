from abc import ABC, abstractmethod
from logging import getLogger

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.integrations.ai.provider import AIProvider
from app.models.analysis import Analysis
from app.models.project import Project
from app.models.upload import Upload
from app.modules.ai.context_builder import ContextBuilder
from app.modules.ai.prompt_loader import PromptLoader
from app.modules.ai.schemas import GenerationResponse
from app.modules.analysis import repository as analysis_repository

logger = getLogger(__name__)


_SYSTEM_PROMPTS: dict[str, str] = {
    "summary": "You are a software analysis assistant. Generate a concise project summary in markdown based on the provided data.",
    "file_explanation": "You are a software analysis assistant. Explain the purpose and functionality of the given source file in markdown.",
    "module_explanation": "You are a software analysis assistant. Explain the purpose and structure of the given module in markdown.",
    "architecture": "You are a software analysis assistant. Describe the software architecture of the project in markdown.",
    "technical_debt": "You are a software analysis assistant. Analyse the project for technical debt and quality concerns. Provide a markdown report.",
    "modernization": "You are a software modernization consultant. Provide actionable modernization recommendations in markdown.",
}


def _validate_ownership(db: Session, user_id: int, analysis_id: int) -> Analysis:
    analysis = analysis_repository.get_analysis_by_id(db, analysis_id)
    if analysis is None:
        raise NotFoundException("Analysis")
    upload = db.query(Upload).filter(Upload.id == analysis.upload_id).first()
    if upload is None:
        raise NotFoundException("Analysis")
    project = db.query(Project).filter(Project.id == upload.project_id).first()
    if project is None or project.user_id != user_id:
        raise NotFoundException("Analysis")
    return analysis


class AIService(ABC):
    @abstractmethod
    def generate_summary(self, db: Session, user_id: int, analysis_id: int) -> GenerationResponse: ...
    @abstractmethod
    def generate_file_explanation(self, db: Session, user_id: int, analysis_id: int, file_id: int) -> GenerationResponse: ...
    @abstractmethod
    def generate_module_explanation(self, db: Session, user_id: int, analysis_id: int, module_path: str) -> GenerationResponse: ...
    @abstractmethod
    def generate_architecture(self, db: Session, user_id: int, analysis_id: int) -> GenerationResponse: ...
    @abstractmethod
    def generate_technical_debt(self, db: Session, user_id: int, analysis_id: int) -> GenerationResponse: ...
    @abstractmethod
    def generate_modernization(self, db: Session, user_id: int, analysis_id: int) -> GenerationResponse: ...


class DefaultAIService(AIService):
    def __init__(self, provider: AIProvider, context_builder: ContextBuilder, prompt_loader: PromptLoader):
        self._provider = provider
        self._context_builder = context_builder
        self._prompt_loader = prompt_loader

    def generate_summary(self, db: Session, user_id: int, analysis_id: int) -> GenerationResponse:
        _validate_ownership(db, user_id, analysis_id)
        context = self._context_builder.build_summary_context(db, analysis_id)
        prompt = self._prompt_loader.render("summary.jinja2", context)
        content = self._provider.generate(prompt, system_prompt=_SYSTEM_PROMPTS["summary"])
        return GenerationResponse(analysis_id=analysis_id, feature="summary", content=content, model=self._provider.model_name)

    def generate_file_explanation(self, db: Session, user_id: int, analysis_id: int, file_id: int) -> GenerationResponse:
        _validate_ownership(db, user_id, analysis_id)
        context = self._context_builder.build_file_explanation_context(db, analysis_id, file_id)
        prompt = self._prompt_loader.render("file_explanation.jinja2", context)
        content = self._provider.generate(prompt, system_prompt=_SYSTEM_PROMPTS["file_explanation"])
        return GenerationResponse(analysis_id=analysis_id, feature="file_explanation", content=content, model=self._provider.model_name)

    def generate_module_explanation(self, db: Session, user_id: int, analysis_id: int, module_path: str) -> GenerationResponse:
        _validate_ownership(db, user_id, analysis_id)
        context = self._context_builder.build_module_explanation_context(db, analysis_id, module_path)
        prompt = self._prompt_loader.render("module_explanation.jinja2", context)
        content = self._provider.generate(prompt, system_prompt=_SYSTEM_PROMPTS["module_explanation"])
        return GenerationResponse(analysis_id=analysis_id, feature="module_explanation", content=content, model=self._provider.model_name)

    def generate_architecture(self, db: Session, user_id: int, analysis_id: int) -> GenerationResponse:
        _validate_ownership(db, user_id, analysis_id)
        context = self._context_builder.build_architecture_context(db, analysis_id)
        prompt = self._prompt_loader.render("architecture.jinja2", context)
        content = self._provider.generate(prompt, system_prompt=_SYSTEM_PROMPTS["architecture"])
        return GenerationResponse(analysis_id=analysis_id, feature="architecture", content=content, model=self._provider.model_name)

    def generate_technical_debt(self, db: Session, user_id: int, analysis_id: int) -> GenerationResponse:
        _validate_ownership(db, user_id, analysis_id)
        context = self._context_builder.build_technical_debt_context(db, analysis_id)
        prompt = self._prompt_loader.render("technical_debt.jinja2", context)
        content = self._provider.generate(prompt, system_prompt=_SYSTEM_PROMPTS["technical_debt"])
        return GenerationResponse(analysis_id=analysis_id, feature="technical_debt", content=content, model=self._provider.model_name)

    def generate_modernization(self, db: Session, user_id: int, analysis_id: int) -> GenerationResponse:
        _validate_ownership(db, user_id, analysis_id)
        context = self._context_builder.build_modernization_context(db, analysis_id)
        prompt = self._prompt_loader.render("modernization.jinja2", context)
        content = self._provider.generate(prompt, system_prompt=_SYSTEM_PROMPTS["modernization"])
        return GenerationResponse(analysis_id=analysis_id, feature="modernization", content=content, model=self._provider.model_name)

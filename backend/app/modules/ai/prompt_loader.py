from dataclasses import asdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class PromptLoader:
    def __init__(self, prompt_dir: str | Path | None = None):
        self._dir = Path(prompt_dir) if prompt_dir else self._default_dir()
        self._env = Environment(
            loader=FileSystemLoader(str(self._dir)),
            autoescape=False,
        )
        self._cache: dict[str, object] = {}

    def render(self, template_name: str, context: object) -> str:
        template = self._cache.get(template_name)
        if template is None:
            try:
                template = self._env.get_template(template_name)
            except TemplateNotFound:
                raise FileNotFoundError(
                    f"Prompt template '{template_name}' not found in {self._dir}"
                )
            self._cache[template_name] = template
        if hasattr(context, "__dataclass_fields__"):
            data = asdict(context)
        elif isinstance(context, dict):
            data = context
        else:
            data = context
        return template.render(**data)

    @staticmethod
    def _default_dir() -> Path:
        return Path(__file__).resolve().parent / "prompts"

    @property
    def template_dir(self) -> Path:
        return self._dir

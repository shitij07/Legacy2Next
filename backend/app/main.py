from fastapi import FastAPI

from app.core.config import settings
from app.modules.auth.routes import router as auth_router
from app.modules.projects.routes import router as projects_router

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.include_router(auth_router)
app.include_router(projects_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules.ai.routes import router as ai_router
from app.modules.analysis.routes import router as analysis_router
from app.modules.auth.routes import router as auth_router
from app.modules.projects.routes import router as projects_router
from app.modules.reports.routes import router as reports_router
from app.modules.uploads.routes import router as uploads_router

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)
app.include_router(analysis_router)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(reports_router)
app.include_router(uploads_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.files import router as files_router
from app.api.flows import router as flows_router
from app.api.nodes import router as nodes_router
from app.core.settings import get_settings
from app.models.health import HealthResponse

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(flows_router)
app.include_router(files_router)
app.include_router(nodes_router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
	return HealthResponse(ok=True)
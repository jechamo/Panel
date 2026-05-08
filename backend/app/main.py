from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
	return HealthResponse(ok=True)
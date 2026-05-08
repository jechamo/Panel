from fastapi import FastAPI

from app.core.settings import get_settings
from app.models.health import HealthResponse

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
	return HealthResponse(ok=True)
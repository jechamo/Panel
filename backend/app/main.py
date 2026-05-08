from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import execute, files, flows, settings
from .db import init_db


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title="Panel")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(flows.router)
    app.include_router(settings.router)
    app.include_router(files.router)
    app.include_router(execute.router)

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True}

    return app


app = create_app()

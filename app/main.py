from fastapi import FastAPI

from app.api import routes_ask, routes_documents, routes_health, routes_operations
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API de copiloto de IA para operaciones agricolas. Combina RAG sobre documentos agronomicos "
            "con datos simulados de parcelas, sensores, incidencias y alertas."
        ),
    )

    app.include_router(routes_health.router)
    app.include_router(routes_ask.router)
    app.include_router(routes_documents.router)
    app.include_router(routes_operations.router)

    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {"name": settings.app_name, "docs": "/docs", "health": "/health"}

    return app


app = create_app()

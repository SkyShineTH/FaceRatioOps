from pathlib import Path
from time import perf_counter

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.metrics import MetricsRegistry

# Built React (Vite) frontend output. Produced by `cd frontend && npm run build`
# and, in production, by the Docker frontend build stage.
STATIC_DIST = Path(__file__).resolve().parent / "static_dist"
SPA_INDEX = STATIC_DIST / "index.html"


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Privacy-first AI inference API for facial geometry analysis.",
    )
    app.state.metrics = MetricsRegistry()
    app.mount("/static_dist", StaticFiles(directory=STATIC_DIST), name="static_dist")

    @app.get("/", include_in_schema=False)
    def frontend() -> FileResponse:
        return FileResponse(SPA_INDEX)

    @app.middleware("http")
    async def record_request_metrics(request, call_next):
        started_at = perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        path = getattr(route, "path", None) or "<unmatched>"
        app.state.metrics.record_request(
            method=request.method,
            path=path,
            status_code=response.status_code,
            duration_seconds=perf_counter() - started_at,
        )
        return response

    app.include_router(router)

    # SPA fallback: client-side routes (e.g. /architecture) must return the app shell.
    # Registered last so explicit API routes and mounts take precedence.
    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str) -> FileResponse:  # noqa: ARG001
        return FileResponse(SPA_INDEX)

    return app


app = create_app()

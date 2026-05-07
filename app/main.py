from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.metrics import MetricsRegistry


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Privacy-first AI inference API for facial geometry analysis.",
    )
    app.state.metrics = MetricsRegistry()

    @app.middleware("http")
    async def record_request_metrics(request, call_next):
        from time import perf_counter

        started_at = perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        app.state.metrics.record_request(
            method=request.method,
            path=path,
            status_code=response.status_code,
            duration_seconds=perf_counter() - started_at,
        )
        return response

    app.include_router(router)
    return app


app = create_app()

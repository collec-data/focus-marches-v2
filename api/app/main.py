from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware

from .router.api_router import api_router

app = FastAPI(
    title="Focus Marche V2",
    root_path="/api",
    dependencies=[],
    generate_unique_id_function=lambda route: route.name,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    # On ajoute le header Cache-Control: no-store sur toutes les routes sauf la doc d'API.
    if not request.url.path.startswith("/docs"):
        response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(api_router)


@app.get("/health", include_in_schema=False)
def health_check() -> dict[str, str]:
    """
    Health-check simple pour permettre de vérifier le lancement de l'API.
    """
    return {"status": "UP"}

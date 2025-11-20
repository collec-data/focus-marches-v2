from fastapi import FastAPI

from .router.api_router import api_router

app = FastAPI(
    title="Focus Marche V2",
    root_path="/api",
    dependencies=[],
    generate_unique_id_function=lambda route: route.name,
)

app.include_router(api_router)


@app.get("/health", include_in_schema=False)
def health_check() -> dict[str, str]:
    """
    Health-check simple pour permettre de vérifier le lancement de l'API.
    """
    return {"status": "UP"}

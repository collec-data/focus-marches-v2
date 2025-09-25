from fastapi import FastAPI

from .config import get_config
from .router.api_router import api_router


app = FastAPI(
    title="Focus Marche V2", root_path=get_config().API_ROOT_PATH, dependencies=[]
)

app.include_router(api_router)


@app.get("/health", include_in_schema=False)
def health_check():
    """
    Health-check simple pour permettre de vérifier le lancement de l'API.
    """
    return {"status": "UP"}

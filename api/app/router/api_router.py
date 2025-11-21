from fastapi import APIRouter

from . import (
    concession_router,
    erreurs_import_router,
    lieu_router,
    marche_router,
    structure_router,
)

api_router = APIRouter()

api_router.include_router(erreurs_import_router.router, prefix="/erreurs-import")
api_router.include_router(marche_router.router, prefix="/marche")
api_router.include_router(concession_router.router, prefix="/contrat-concession")
api_router.include_router(structure_router.router, prefix="/structure")
api_router.include_router(lieu_router.router, prefix="/lieu")

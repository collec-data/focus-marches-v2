from fastapi import APIRouter

from . import (
    concession_router,
    cpv_router,
    erreurs_import_router,
    lieu_router,
    marche_router,
)
from .conf import conf_router
from .structure.router import router as structure_router

api_router = APIRouter()

api_router.include_router(erreurs_import_router.router, prefix="/erreurs-import")
api_router.include_router(marche_router.router, prefix="/marche")
api_router.include_router(concession_router.router, prefix="/contrat-concession")
api_router.include_router(structure_router, prefix="/structure")
api_router.include_router(lieu_router.router, prefix="/lieu")
api_router.include_router(cpv_router.router, prefix="/cpv")
api_router.include_router(conf_router.router, prefix="/conf")

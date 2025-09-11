from fastapi import APIRouter

from . import erreurs_import_router, marche_router, concession_router

api_router = APIRouter()

api_router.include_router(erreurs_import_router.router, prefix="/erreurs-import")
api_router.include_router(marche_router.router, prefix="/marche")
api_router.include_router(concession_router.router, prefix="/contrat-concession")

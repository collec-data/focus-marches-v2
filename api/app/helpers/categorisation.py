from app.models.enums import CategorieMarche


def CPV2categorie(cpv: str) -> CategorieMarche:
    if cpv[0:2] == "45":
        return CategorieMarche.TRAVAUX

    if int(cpv[0:2]) >= 50:
        return CategorieMarche.SERVICES

    return CategorieMarche.FOURNITURES

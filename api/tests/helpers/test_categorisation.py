from app.helpers.categorisation import CPV2categorie
from app.models.enums import CategorieMarche


def test_categorisation():
    assert CPV2categorie("45000000-7") == CategorieMarche.TRAVAUX
    assert CPV2categorie("45200000-9") == CategorieMarche.TRAVAUX

    assert CPV2categorie("30200000-1") == CategorieMarche.FOURNITURES
    assert CPV2categorie("33600000-6") == CategorieMarche.FOURNITURES

    assert CPV2categorie("79400000-8") == CategorieMarche.SERVICES
    assert CPV2categorie("60100000-9") == CategorieMarche.SERVICES

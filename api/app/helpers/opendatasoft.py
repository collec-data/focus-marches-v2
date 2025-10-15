import requests


class OpenDataSoft:
    BASE_URL: str = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/economicref-france-sirene-v3/"

    def getCoordonnees(self, siret: str) -> dict[str, int | None]:
        response = requests.get(f"{self.BASE_URL}records?where=siret%3D{siret}")

        if not response.status_code == 200:
            return {"lon": None, "lat": None}

        geoloc = response.json()["results"][0]["geolocetablissement"]
        return {"lon": geoloc["lon"], "lat": geoloc["lat"]}


def get_opendatasoft() -> OpenDataSoft:
    return OpenDataSoft()

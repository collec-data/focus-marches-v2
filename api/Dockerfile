
FROM python:3.14.4-alpine@sha256:01f125438100bb6b5770c0b1349e5200b23ca0ae20a976b5bd8628457af607ae

EXPOSE 80
WORKDIR /code

RUN apk add --no-cache build-base curl mariadb mariadb-dev

COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt && apk del --no-cache build-base

COPY ./app /code/app
COPY ./cpv_2008_fr.csv /code/cpv_2008_fr.csv

# EXPOSE
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80" ]

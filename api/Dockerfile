
FROM python:3.14.4-alpine@sha256:dd4d2bd5b53d9b25a51da13addf2be586beebd5387e289e798e4083d94ca837a

EXPOSE 80
WORKDIR /code

RUN apk add --no-cache build-base curl mariadb mariadb-dev

COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt && apk del --no-cache build-base

COPY ./app /code/app
COPY ./cpv_2008_fr.csv /code/cpv_2008_fr.csv

# EXPOSE
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80" ]

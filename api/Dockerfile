
FROM python:3.14.3-alpine@sha256:faee120f7885a06fcc9677922331391fa690d911c020abb9e8025ff3d908e510

EXPOSE 80
WORKDIR /code

RUN apk add --no-cache build-base curl mariadb mariadb-dev

COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt && apk del --no-cache build-base

COPY ./app /code/app
COPY ./cpv_2008_fr.csv /code/cpv_2008_fr.csv

# EXPOSE
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80" ]

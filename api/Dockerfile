
FROM python:3.14.5-alpine@sha256:5a824eb82cc75361f98611f3cfc5091ea33f10a6ccea4d4ebdabbc523b9a1614

EXPOSE 80
WORKDIR /code

RUN apk add --no-cache build-base curl mariadb mariadb-dev

COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt && apk del --no-cache build-base

COPY ./app /code/app
COPY ./cpv_2008_fr.csv /code/cpv_2008_fr.csv

# EXPOSE
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80" ]

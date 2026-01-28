
FROM python:3.14.2-alpine@sha256:59d996ce35d58cbe39f14572e37443a1dcbcaf6842a117bc0950d164c38434f9

EXPOSE 80
WORKDIR /code
COPY requirements.txt /code/requirements.txt

RUN apk add --no-cache build-base \
  && pip install -r requirements.txt \
  && apk del --no-cache build-base \
  # add curl for healthcheck
  && apk add --no-cache curl

COPY ./app /code/app
COPY ./cpv_2008_fr.csv /code/cpv_2008_fr.csv

# EXPOSE
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80" ]

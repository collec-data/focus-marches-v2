
FROM python:3.12.9-alpine

EXPOSE 80
WORKDIR /code
COPY requirements.txt /code/requirements.txt

RUN apk add --no-cache build-base \
  && pip install -r requirements.txt \
  && apk del --no-cache build-base \
  # add curl for healthcheck
  && apk add --no-cache curl

COPY ./app /code/app

# EXPOSE
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80" ]

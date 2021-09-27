FROM python:3.9-alpine

ENV FLASK_APP=main.py TZ=Europe/Moscow

RUN adduser -D ppuser
WORKDIR /home/pointparser

ADD requirements.txt requirements.txt
ADD app app
# ADD tests tests TODO
ADD migrations migrations
ADD config.py config.py
ADD main.py main.py
ADD sh sh

RUN apk update && apk upgrade && pip3 install --upgrade pip

RUN apk add --no-cache postgresql-libs tzdata && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
#     python3 -m pip install sphinx sphinx-rtd-theme --no-cache-dir && \
    apk --purge del .build-deps && \
    chown -R ppuser:ppuser *

USER ppuser

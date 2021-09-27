FROM postgres:12.6

ENV POSTGRES_HOST_AUTH_METHOD trust

RUN apt-get update \
    && apt-get install wget -y \
    && apt-get install postgresql-12-postgis-3 -y \
    && apt-get install postgis -y

ADD ./pointparser.dump /tmp/
ADD init_database.sql /docker-entrypoint-initdb.d

WORKDIR .


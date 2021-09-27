DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'ppuser') THEN
      CREATE ROLE ppuser with NOSUPERUSER LOGIN PASSWORD 'Qwert!2345';
   END IF;
END
$do$;

--создание БД и схем
SELECT 'CREATE DATABASE pointparser' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pointparser')\gexec
\connect pointparser;

--\i /tmp/pointparser.dump;

CREATE SCHEMA IF NOT EXISTS authentication;
CREATE SCHEMA IF NOT EXISTS common;
CREATE SCHEMA IF NOT EXISTS locations;
CREATE SCHEMA IF NOT EXISTS parsers;
CREATE SCHEMA IF NOT EXISTS points;

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER DATABASE sneg OWNER TO ppuser;
ALTER SCHEMA authentication OWNER TO ppuser;
ALTER SCHEMA common OWNER TO ppuser;
ALTER SCHEMA locations OWNER TO ppuser;
ALTER SCHEMA parsers OWNER TO ppuser;
ALTER SCHEMA points OWNER TO ppuser;

\q

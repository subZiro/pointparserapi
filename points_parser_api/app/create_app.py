"""
Создание приложения
"""

from config import config
from flask import Flask, Blueprint
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restplus import Api, apidoc
from flask_sqlalchemy import SQLAlchemy

from celery import Celery


def make_alembic(application: Flask, data_base: SQLAlchemy) -> Migrate:
    """
    create Migrate application

    :param flask application:
    :param data_base application:
    :return: Migrate application:
    """
    from app.common import render_item, include_object

    migrate_ = Migrate(app=application,
                       db=data_base,
                       include_schemas=True,
                       render_item=render_item,
                       include_object=include_object)

    return migrate_


def make_celery(application: Flask) -> Celery:
    """
    create Celery application

    :param flask application:
    :return: celery application:
    """
    celery_ = Celery(
        application.import_name,
        backend=application.config['RESULT_BACKEND'],
        broker=application.config['CELERY_BROKER_URL'],
        include=application.config["INSTALLED_APPS"],
        task_track_started=True,
    )
    celery_.conf.update(application.config)

    class ContextTask(celery_.Task):
        def __call__(self, *args, **kwargs):
            with application.app_context():
                return self.run(*args, **kwargs)

    celery_.Task = ContextTask
    return celery_


def make_application(config_name: str):
    """
    Создание приложение

    :param config_name: str: config name
    :return: tuple: flask application, celery application, flask migrate
    """
    application = Flask(__name__)
    CORS(application, support_credentials=True)
    application.config.from_object(config[config_name])
    config[config_name].init_app(application)

    if application.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        SSLify(application)

    from app import db
    db.init_app(application)

    celery = make_celery(application)

    alembic = make_alembic(application, db)

    apidoc.apidoc.url_prefix = '/api/v1'
    authorizations = {'apikey': {'type': 'apiKey',
                                 'in': 'header',
                                 'name': 'Authorization'}
                      }

    from app.api_v1.auth import authenticate
    api_ = Blueprint('api_v1', __name__)
    api = Api(application,
              doc='/api/v1/docs/',
              title=f'PP. Flask-restplus Swagger API v1. stage {config[config_name].ENV}',
              version='1.01',
              prefix='/api/v1',
              default="PP",
              default_label="backend",
              authorizations=authorizations,
              security="apikey",
              decorators=[authenticate],
              )
    api.namespaces.clear()
    application.register_blueprint(api_)

    return application, celery, alembic, api

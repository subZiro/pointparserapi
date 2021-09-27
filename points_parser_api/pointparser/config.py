import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Базовый конфигурационный класс приложения

    """
    API_VERSION = 'v1'
    HOST_URL = 'http://localhost:5000'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL', 'postgresql://ppuser:Qwert!2345@localhost/pointparser')

    EXCLUDE_TABLES = ('spatial_ref_sys', 'layer', 'topology')

    YANDEX_API_URL = "https://geocode-maps.yandex.ru/1.x?apikey={}"
    YANDEX_API_TOKEN = os.environ.get('YANDEX_API_TOKEN')
    SEARCH_MAP_TOKEN = os.environ.get('SEARCH_MAP_TOKEN')

    LATLNG_REDSQARE = [55.750682, 37.615321]

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = bool(os.environ.get('MAIL_USE_TLS', True))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    PP_MAIL_SUBJECT_PREFIX = '[PointParser]'
    PP_MAIL_SENDER = 'PP Admin <info@pointparser.com>'
    PP_ADMIN = os.environ.get('PP_APP_ADMIN')

    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    DATE_TMPL = "%Y-%m-%dT%H:%M:%S"

    TASK_ACKS_LATE = True
    WORKER_PREFETCH_MULTIPLIER = 1
    TIMEZONE = 'Europe/Moscow'
    CELERY_ENABLE_UTC = True
    TASK_SERIALIZER = 'json'
    RESULT_SERIALIZER = 'json'
    ACCEPT_CONTENT = ['application/json']
    INSTALLED_APPS = ['app.celery.celery_tasks', ]
    TASK_NORMALIZE = (18, 0, '*')  # (часы, минуты, дни)  # UTC+3 = MSK
    TASK_QUEUE = ('schedulerq', 'workerq')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """DEV"""
    ENV = 'development'
    DEBUG = True
    CELERY_BROKER_URL = os.environ.get('DEV_CELERY_BROKER_URL')
    RESULT_BACKEND = os.environ.get('DEV_RESULT_BACKEND')


class TestingConfig(Config):
    """TEST"""
    ENV = 'testing'
    TESTING = True
    CELERY_BROKER_URL = os.environ.get('TEST_CELERY_BROKER_URL')
    RESULT_BACKEND = os.environ.get('TEST_RESULT_BACKEND')


class ProductionConfig(Config):
    """PROD"""
    ENV = 'production'
    CELERY_BROKER_URL = os.environ.get('PROD_CELERY_BROKER_URL')
    RESULT_BACKEND = os.environ.get('PROD_RESULT_BACKEND')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {'development': DevelopmentConfig,
          'testing': TestingConfig,
          'production': ProductionConfig,
          'default': DevelopmentConfig, }

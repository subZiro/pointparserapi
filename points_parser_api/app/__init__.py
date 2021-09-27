import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

if __name__ != "__main__":
    from app.create_app import make_application

    app, celery_app, migrate, api = make_application(os.getenv('FLASK_CONFIG', 'default'))
    from app.api_v1.routes import namespace

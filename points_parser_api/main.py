"""
PointParser app
"""

from flask_migrate import upgrade

from app import app, celery_app


@app.shell_context_processor
def make_shell_context() -> dict:
    """
    Создание контекста в консоли

    :return: dict
    """
    from app import db
    from app.models import User, UserRole
    return {'db': db, 'User': User, 'Role': UserRole}


@app.cli.command('deploy')
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()

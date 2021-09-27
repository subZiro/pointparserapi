"""
Контроллеры Авторизации/Аутентификации
"""

from flask import g
from app.errors import unauthorized, forbidden
from app.models import User
from functools import wraps
from flask import request


def authenticate(view_function):
    """
    Декоратор аторизации на сервере
    """

    @wraps(view_function)
    def decorator(*args, **kwargs):

        if request.path.endswith("swagger.json"):
            return view_function(*args, **kwargs)

        token = request.headers.get('Authorization', None)
        if not token:
            return unauthorized(message='Token is missing')

        if verify_token(token=token):  # валидация токена
            return view_function(*args, **kwargs)
        else:
            return forbidden()

    return decorator


def verify_token(token: str):
    """
    Верификайия пользователя по токену

    :param token: str
    :return: bool: true - токен подтвержден
    """

    if not token or token == '':
        return False
    g.current_user = User.verify_auth_token(token)
    g.token_used = True

    return g.current_user is not None

"""
Декораторы
"""

from flask import g
from functools import wraps

from app.errors import bad_request


def permission_required(permission):
    """Декоратор доступа для permission группы пользователей"""

    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            if g is None or g.current_user.role_id <= permission:
                return view_function(*args, **kwargs)
            return bad_request(message='У вас нет доступа для изменений. Обратитесь к администратору!')

        return decorated_function

    return decorator


def admin_required(view_function):
    """Декоратор доступа пользователей с ролью администраторам."""
    # 1 = admin
    return permission_required(1)(view_function)


def manager_required(view_function):
    """Декоратор доступа пользователей с ролью менедреж и выше."""
    # 2 = manager
    return permission_required(2)(view_function)

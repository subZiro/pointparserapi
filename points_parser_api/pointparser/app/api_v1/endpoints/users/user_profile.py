"""
Контролеры раздела Пользователи
"""

from flask import g
from flask_restplus import Resource

from app import db, api
from app.models import User, UserRole
from app.errors import not_found, bad_request
from app.api_v1.common import ValidateMixin, create_response


class UserProfileCrud(ValidateMixin, Resource):

    def __init__(self, *args, **kwargs):
        super(UserProfileCrud, self).__init__(*args, **kwargs)

    @api.doc()
    def get(self):
        """
        Профиль авторизированного пользователя

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' == ""
        * 'data' - Словарь данных по пользователю
        """

        return create_response({
            "id": str(g.current_user.uid),
            "role_id": g.current_user.role_id,
            "email": g.current_user.email,
            "caption": g.current_user.caption,
            "description": g.current_user.description,
            "last_seen": str(g.current_user.last_seen),
        })

from flask import g, request
from flask_restplus import Resource

from sqlalchemy import DATE

from app import db, api
from app.models import User, UserRole
from app.errors import bad_request
from app.api_v1.common import ValidateMixin, create_response, sort_by, prep_search
from app.api_v1.resource_models import post_fields


class UsersCrud(ValidateMixin, Resource):
    """Контролеры раздела Пользователи."""

    def __init__(self, *args, **kwargs):
        super(UsersCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())
        self.data_flg = self.validate_post_key(request.get_json(), ['offset', 'limit', 'sort'])
        _data = request.get_json()
        if self.data_flg:
            self.offset = int(_data['offset'])
            self.limit = int(_data['limit'])
            self.sort = _data['sort']
            self.download = bool(_data.get('download', False))
            self.filters = _data.get('filter', dict())

    @api.doc(body=post_fields())
    def post(self):
        """
        Список зарегистрированных пользователей в системе

        **Описание возвращаемого соощения**
        **При успешном получении массива пользователей**
        * 'code' == 200
        * 'message' == ""
        * 'data' == {'limit': int, offset': int, 'total': int, 'data': list(Список словарей пользователей)}
        """

        if not self.data_flg:  # проверка корректности введеных данных
            return bad_request(message='Отсутствует обязательное поле или пустое значение')

        query = db.session.query(
            User.pid.label('id'),
            User.email,
            User.last_seen,
            User.member_since,
            User.is_active,
            User.caption,
            User.description,
            User.role_id,
            UserRole.caption.label('role_name'),
        ) \
            .select_from(User) \
            .join(UserRole, UserRole.pid == User.role_id) \
            .order_by(sort_by(self.sort))

        search = {}
        fields = get_users_fields()
        query = prep_search(query, fields, self.filters, search)

        user_role = g.current_user.role_id
        if user_role != 1:  # админы видят всех пользователей
            query = query.filter(UserRole.pid == user_role)

        data = {
            'offset': self.offset,
            'limit': self.limit,
            'total': query.count(),
            'data': [{'id': x.id,
                      'email': x.email,
                      'role': {'id': x.role_id, 'name': x.role_name},
                      'is_active': x.is_active,
                      'member_since': x.member_since,
                      'last_seen': x.last_seen,
                      'caption': x.caption,
                      'description': x.description,
                      } for x in query.offset(self.offset).limit(self.limit)]
        }

        return create_response(data=data)


def get_users_fields() -> dict:
    """
    Словарь с возможными фильтрами к разделу Пользователи

    :return: dict
    """

    return {'email': User.email.ilike,
            'role_id': ('list', UserRole.pid),
            'role_name': UserRole.caption.ilike,
            'caption': User.caption.ilike,
            'description': User.description.ilike,
            'is_active': ('bool', User.is_active),
            'member_since': ('date', User.member_since.cast(DATE)),
            'last_seen': ('date', User.last_seen.cast(DATE)),
            }

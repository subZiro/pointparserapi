from datetime import datetime
from flask import g, request
from flask_restplus import Resource

from app import db, api
from app.models import User

from app.errors import bad_request
from app.database import db_add, db_delete
from app.api_v1.decorators import admin_required

from app.api_v1.common import ValidateMixin, create_response
from app.api_v1.resource_models import user_create_fields


class UserCreateCrud(ValidateMixin, Resource):
    """Создание нового пользователя."""

    def __init__(self, *args, **kwargs):
        super(UserCreateCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())
        self.data_flg = self.validate_post_key(request.get_json(), ['email', 'role_id', 'caption', ])
        if self.data_flg:
            self._data = request.get_json()

    @admin_required
    @api.doc(body=user_create_fields())
    def post(self):
        """
        Создание нового пользователя

        **Описание возвращаемого соощения**
        **При успешном создании пользователя**
        * 'code' == 200
        * 'message' - Сообщение с успешным созданием
        * 'data' == {}
        """

        if not self.data_flg:  # проверка корректности введеных данных
            return bad_request(message='Отсутствует обязательное поле или пустое значение')

        user = db.session.query(User).filter_by(email=self._data['email']).first()
        if user is not None:
            return bad_request(f'Пользователь с таким email=[{self._data["email"]}] уже существует')

        new_user = User(email=self._data['email'],
                        role_id=self._data['role_id'],
                        caption=self._data['caption'],
                        member_since=datetime.now(),
                        last_seen=None,
                        )

        flg = False
        if db_add(new_user):
            flg = new_user.update_row(data=self._data)  # запись данных пользователя

        if flg:
            return create_response(data={}, message=f'Успешно создан новый пользователь id=[{new_user.pid}]!')
        else:
            db_delete(new_user)
            return bad_request(message='Ошибка создания нового пользователя!')

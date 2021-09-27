from flask import g, request
from flask_restplus import Resource

from app import db, api
from app.models import User
from app.errors import not_found, bad_request
from app.api_v1.decorators import admin_required
from app.api_v1.common import ValidateMixin, create_response
from app.api_v1.resource_models import user_update_fields


class UserUpdateCrud(ValidateMixin, Resource):
    """
    Список холодильного оборудования в системе
    """

    def __init__(self, *args, **kwargs):
        super(UserUpdateCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())
        self.data_flg = self.validate_post_key(request.get_json(), ['user_id', ])
        if self.data_flg:
            self._data = request.get_json()

    @admin_required
    @api.doc(body=user_update_fields())
    def post(self):
        """
        Редактирование пользователя администратором или руководителем

        **Описание возвращаемого соощения**
        **При успешном изменении**
        * 'code' == 200
        * 'message' - Сообщение с успешным обновлением данных
        * 'data' == {}
        """

        if not self.data_flg:  # проверка корректности введеных данных
            return bad_request(message='Отсутствует обязательное поле или пустое значение для [user_id]')

        user_id = self._data['user_id']
        user = db.session.query(User).filter_by(pid=user_id).first()
        if user is None:
            return not_found(message=f'Не удалось найти пользователя с user_id=[{user_id}]')

        flg = user.update_row(data=self._data)  # запись данных пользователя
        if flg:
            return create_response(data={}, message=f'Успешно изменены данные пользователя caption=[{user.caption}]')
        else:
            return bad_request(message=f'Ошибка при изменении данных пользователя user_id=[{user_id}]')

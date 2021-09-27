from flask_restplus import Resource

from app import db, api
from app.models import User
from app.errors import not_found
from app.api_v1.common import ValidateMixin, create_response


class UserTokenCrud(ValidateMixin, Resource):
    """Токен пользователя."""

    def __init__(self, *args, **kwargs):
        super(UserTokenCrud, self).__init__(*args, **kwargs)

    @api.doc()
    def get(self, idx):
        """
        Получение токена польхователя

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' == ""
        * 'data' - Словарь данных по пользователю
        """

        user = db.session.query(
            User.pid.label('id'),
            User.uid.label('token'),
            User.caption,
            User.last_seen,
            User.member_since,
        ) \
            .select_from(User) \
            .filter(User.pid == idx) \
            .first()

        if user is not None:
            data = {
                'id': user.id,
                'token': user.token,
                'caption': user.caption,
                'last_seen': user.last_seen,
                'member_since': user.member_since,
            }
            return create_response(data=data)
        else:
            return not_found(message='Пользователь не найден!')

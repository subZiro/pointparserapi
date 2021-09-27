"""
Контролеры приветствия к апи
"""

from flask import request, current_app
from flask_restplus import Resource

from app import api
from app.api_v1.common import create_response


class MainPage(Resource):

    def __init__(self, *args, **kwargs):
        super(MainPage, self).__init__(*args, **kwargs)

    @staticmethod
    @api.doc()
    def get():
        """
        Приветствие API

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' - приветствие с указанием стадии api
        * 'data' == {}
        """

        return create_response(data={}, message=f"Welcome to {current_app.config['ENV']} stage, PP API!")

"""
Методы работы с файлами
"""

import io
import datetime
import logging
import xlsxwriter

from itertools import chain
from base64 import b64encode
from flask import send_file
from collections.abc import Iterable

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app.processing_files')


def create_excel(filename: str, data: Iterable, header: Iterable = None, not_send: bool = None, sales: dict = None,
                 to_save: bool = False):
    """
    Создание excel документа из массива данных data

    :param filename: str:
    :param data: list:
    :param header: list or None:
    :param not_send: bool or None:
    :param sales: dict or None:
    :param to_save: bool:
    :return:
    """
    xlsx = io.BytesIO()
    header = header or []
    workbook = xlsxwriter.Workbook(xlsx, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    datetime_type = datetime.datetime
    date_type = datetime.date

    except_types = (list, dict)

    for row_num, row_val in enumerate(chain(header, data), start=1):

        if sales is not None and row_num != 1:
            outlet_id = row_val[0] if type(row_val) == tuple else row_val.outlet_id
            row_val = chain(row_val, sales[outlet_id].values())

        for col_num, col_val in enumerate(row_val):
            type_val = type(col_val)

            if type_val in except_types:
                continue

            if type_val in (date_type, datetime_type):
                col_val = col_val.strftime("%Y-%m-%d")

            worksheet.write(row_num, col_num, col_val)

    workbook.close()
    xlsx.seek(0)

    if to_save:
        # сохранение в файл на сервере
        with open(filename, "wb") as f:
            f.write(xlsx.getbuffer())

    if not_send:
        # возвращает контент файла в виде строки(base64)
        return b64encode(xlsx.getvalue()).decode()

    return send_file(xlsx, attachment_filename=f'{filename}.xlsx', as_attachment=True)

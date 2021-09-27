"""
Получение парсера
"""

import logging

from app import db
from app.models import ParserDetail

logger = logging.getLogger('app.parsers.parser')
logger.setLevel(logging.DEBUG)


def get_parser(parser_type: str) -> ParserDetail or None:
    """
    Получение парсера

    :param parser_type: str
    :return parser: ParserDetail or None
    """
    parser = db.session.query(ParserDetail).filter_by(parser_type=parser_type).first()
    if parser is None:
        logging.error(f'get_parser. ERROR. Не создан парсер "{parser_type}" в parsers.tb_parsers_details')
    return parser

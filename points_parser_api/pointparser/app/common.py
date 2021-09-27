"""
Вспомогательные методы приложения
"""

import contextlib
import logging
import sys
from base64 import b64encode
from os import path
from typing import Any

import requests
from config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app.common')


def render_item(type_, obj, autogen_context):
    """Apply custom rendering for selected items."""

    # if type_ == 'type' and isinstance(obj, MySpecialType):
    #     return "mypackage.%r" % obj

    # default rendering for other objects
    return False


def include_object(obj, name, type_, reflected, compare_to):
    """include object in migration"""
    if type_ == "table" and name in Config.EXCLUDE_TABLES:
        return False

    return True

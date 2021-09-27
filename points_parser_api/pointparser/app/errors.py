"""
Ошибки API
"""


def bad_request(message='Bad request'):
    """
    Response 400

    :param message: str:
    :return: json:
    """
    from app.api_v1.common import create_response
    return create_response(None, 400, message)


def unauthorized(message='unauthorized'):
    """
    Response 401

    :param message: str:
    :return: json:
    """
    from app.api_v1.common import create_response
    return create_response(None, 401, message)


def forbidden(message='forbidden'):
    """
    Response 403

    :param message: str:
    :return: json:
    """
    from app.api_v1.common import create_response
    return create_response(None, 403, message)


def not_found(message='Object not found'):
    """
    Response 404

    :param message: str:
    :return: json:
    """
    from app.api_v1.common import create_response
    return create_response(None, 404, message)

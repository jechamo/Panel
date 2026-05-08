from typing import Any


def error_response(code: str, message: str) -> dict[str, Any]:
    return {
        'ok': False,
        'data': None,
        'error': {
            'code': code,
            'message': message,
        },
    }


def success_response(data: Any) -> dict[str, Any]:
    return {
        'ok': True,
        'data': data,
        'error': None,
    }
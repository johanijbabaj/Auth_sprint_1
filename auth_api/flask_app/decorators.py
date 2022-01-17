from functools import wraps
from http import HTTPStatus

from db_models import User
from flask.json import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


def admin_required():
    """
    Декоратор для функций, которые должны выполняться с правами
    администратора. Благодаря проверке verify_jwt_in_request
    может применяться без декоратора jwt_required, заменяя его
    и добавляя еще одну проверку - что обратившийся пользователь
    входит в группу администраторов. Если не входит - функция
    не выполняется и возвращается ошибка 403.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as ex:
                return (
                    jsonify({"msg": f"Bad access token: {ex}"}),
                    HTTPStatus.UNAUTHORIZED,
                )
            current_user = User.query.get(get_jwt_identity())
            if not current_user or not current_user.is_admin():
                return (
                    jsonify({"error": "Only administrators may do it"}),
                    HTTPStatus.FORBIDDEN,
                )
            return fn(*args, **kwargs)

        return decorated

    return wrapper


# def user_required( ):
#     """
#         Декоратор для функций, которые должны выполняться с правами
#         пользователя. Благодаря проверке verify_jwt_in_request
#         может применяться без декоратора jwt_required, заменяя его
#         и добавляя еще одну проверку - что обратившийся пользователь
#         авторизован через jwt токен и получен id из токена. Если не входит - функция
#         не выполняется и возвращается ошибка 403.
#     """
#     def wrapper(fn):
#         @wraps(fn)
#         def decorated(*args, **kwargs):
#             try:
#                 verify_jwt_in_request()
#             except Exception as ex:
#                 return jsonify({"msg": f"Bad access token: {ex}"}), HTTPStatus.UNAUTHORIZED
#             current_user = User.query.get(get_jwt_identity())
#             if not current_user:
#                 return jsonify({"error": "No such user"}), HTTPStatus.FORBIDDEN
#             return fn(*args, **kwargs)
#
#         return decorated
#
#     return wrapper

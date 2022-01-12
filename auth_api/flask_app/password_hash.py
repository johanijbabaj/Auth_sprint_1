"""
Модуль для хэширования и проверки паролей
"""
import bcrypt


def hash_password(password_str):
    """
    Хэшируем и солим пароли
    :param password_str: Полученный от пользователя пароль
    :return: Хэшированный и засоленный пароль для хранения в базе
    """

    hash_and_salt = bcrypt.hashpw(password_str.encode("utf-8"), bcrypt.gensalt())
    return hash_and_salt.decode("utf-8")


def check_password(password_str, hash_and_salt):
    """
    Проверки корректности пароля
    :param password_str: Введеная строка с паролем для проверки
    :param hash_and_salt: полученный из базы хэш пароля
    :return: Возврашаем реузльат рповерки
    """
    valid = bcrypt.checkpw(password_str.encode("utf-8"), hash_and_salt.encode("utf-8"))
    return valid

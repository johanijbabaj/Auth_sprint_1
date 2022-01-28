import os
import requests
from typing import Optional


def get_user_type(auth_header: Optional[str] = None):
    """
    Определить тип пользователя по его Jwt токену. Возможные
    возаращаемые значения

    - "anonymous" - пользователь не авторизован
    - "free" - пользователь авторизован и не имеет платной подписки
    - "paid" - пользователь авторизован и имеет платную подписку

    Для этого обращается к сервису Auth с переданным JWT токеном.
    Если токен не передан (является None) то возвращается "anonymous".
    Иначе запрашивается список групп пользователя. Если пользователь
    входит в группу subscriber, то возвращается "paid", иначе "free"
    """
    if auth_header is None:
        return "anonymous"
    auth_api_host = os.getenv("AUTH_API_HOST", "auth_api")
    auth_api_port = os.getenv("AUTH_API_PORT", 5000)
    ans = requests.get(
        f"http://{auth_api_host}:{auth_api_port}/v1/users/groups",
        headers={"Authorization": auth_header},
    )
    if ans.status_code == 200:
        for group in ans.json():
            if group["name"] == "subscriber":
                return "paid"
        return "free"
    else:
        return "anonymous"

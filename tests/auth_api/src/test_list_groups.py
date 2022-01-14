import os

import pytest
import requests

AUTH_API_HOST = os.getenv("AUTH_API_HOST", "flask_auth_api:5000")


def test_group_list():
    ans = requests.get(f"http://{AUTH_API_HOST}/v1/group/")
    assert ans.status_code == 200
    data = ans.json()
    assert isinstance(data, list)


def test_create_group_no_permissions():
    """Незарегистрированный пользователь не может создать группу"""
    gid = "23977ba2-70b9-11ec-8215-83c9c808fe75"
    gname = "Тестовая группа"
    gdescription = "Тестовая группа"
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/group/",
        json={"id": gid, "name": gname, "description": gdescription},
    )
    assert ans.status_code in [403, 401]


def test_create_delete_group():
    """
    <<<<<<< HEAD
            Создать группу, убедиться, что она возвращается в списке
            всех групп и удалить ее. Для этого войти как администратор
    =======
        Создать группу, убедиться, что она возвращается в списке
        всех групп и удалить ее
    >>>>>>> main
    """
    gid = "23977ba2-70b9-11ec-8215-83c9c808fe75"
    gname = "Тестовая группа"
    gdescription = "Тестовая группа"
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/user/login?login=admin&password={os.getenv('ADMIN_PASSWORD')}"
    )
    assert ans.status_code == 200
    data = ans.json()
    token = data["access_token"]
    # Запрашиваем группу и проверяем, что ее нет в базе
    ans = requests.get(
        f"http://{AUTH_API_HOST}/v1/group/{gid}/",
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 404
    # Создаем группу
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/groups/",
        json={"id": gid, "name": gname, "description": gdescription},
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 200
    # Запрашиваем группу и проверяем, что теперь она есть
    ans = requests.get(
        f"http://{AUTH_API_HOST}/v1/group/{gid}/",
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 200
    # Удаляем группу
    ans = requests.delete(
        f"http://{AUTH_API_HOST}/v1/group/{gid}/",
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 200
    # Проверяем, что теперь ее снова нет
    ans = requests.get(
        f"http://{AUTH_API_HOST}/v1/group/{gid}/",
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 404


def test_nobody_create_group():
    """Не-администратор не может создавать группу"""
    gid = "23977ba2-70b9-11ec-8215-83c9c808fe75"
    gname = "Тестовая группа"
    gdescription = "Тестовая группа"
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/user/login?login=nobody&password={os.getenv('NOBODY_PASSWORD')}"
    )
    assert ans.status_code == 200
    data = ans.json()
    token = data["access_token"]
    # Запрашиваем группу и проверяем, что ее нет в базе
    ans = requests.get(
        f"http://{AUTH_API_HOST}/v1/group/{gid}/",
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 404
    # Пытаемся создать группу, но должно не получиться
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/groups/",
        json={"id": gid, "name": gname, "description": gdescription},
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code in [401, 403]
    # Проверяем, что ее все еще нет
    ans = requests.get(
        f"http://{AUTH_API_HOST}/v1/group/{gid}/",
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 404
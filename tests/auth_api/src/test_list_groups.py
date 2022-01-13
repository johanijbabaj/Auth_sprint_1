import os
import pytest
import requests

AUTH_API_HOST = os.getenv('AUTH_API_HOST', 'flask_auth_api:5000')


def test_group_list():
    ans = requests.get(f"http://{AUTH_API_HOST}/v1/groups/")
    assert ans.status_code == 200
    data = ans.json()
    assert isinstance(data, list)


def test_create_group_no_permissions():
    """Незарегистрированный пользователь не может создать группу"""
    gid = "23977ba2-70b9-11ec-8215-83c9c808fe75"
    gname = "Тестовая группа"
    gdescription = "Тестовая группа"
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/groups/",
        json={
            'id': gid,
            'name': gname,
            'description': gdescription
        }
    )
    assert ans.status_code in [403, 401]


@pytest.mark.skip("Permissions required")
def test_create_delete_group():
    """
        Создать группу, убедиться, что она возвращается в списке
        всех групп и удалить ее
    """
    gid = "23977ba2-70b9-11ec-8215-83c9c808fe75"
    gname = "Тестовая группа"
    gdescription = "Тестовая группа"
    # Запрашиваем группу и проверяем, что ее нет в базе
    ans = requests.get(f"http://{AUTH_API_HOST}/v1/group/{gid}/")
    assert ans.status_code == 404
    # Создаем группу
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/groups/",
        json={
            'id': gid,
            'name': gname,
            'description': gdescription
        }
    )
    assert ans.status_code == 200
    # Запрашиваем группу и проверяем, что теперь она есть
    ans = requests.get(f"http://{AUTH_API_HOST}/v1/group/{gid}/")
    assert ans.status_code == 200
    # Удаляем группу
    ans = requests.delete(f"http://{AUTH_API_HOST}/v1/group/{gid}/")
    assert ans.status_code == 200
    # Проверяем, что теперь ее снова нет
    ans = requests.get(f"http://{AUTH_API_HOST}/v1/group/{gid}/")
    assert ans.status_code == 404

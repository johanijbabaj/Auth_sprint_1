import os
from uuid import uuid1

import pytest
import requests

AUTH_API_HOST = os.getenv("AUTH_API_HOST", "flask_auth_api:5000")


@pytest.fixture()
def seven_little_guys(request):
    """Создать тестовую группу из семи пользователей"""
    gid = uuid1()
    uids = []
    for _ in range(7):
        uids.append(uuid1())
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/users/login?login=admin&password={os.getenv('ADMIN_PASSWORD')}"
    )
    assert ans.status_code == 200
    data = ans.json()
    token = data["access_token"]
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/groups/",
        json={
            "id": str(gid),
            "name": "Семь гномов",
            "description": "Тестовая группа из семи пользователей",
        },
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 200
    for (i, uid) in enumerate(uids):
        ans = requests.post(
            f"http://{AUTH_API_HOST}/v1/users/register",
            json={
                "id": str(uid),
                "login": f"Dwarf-{i + 1}",
                "email": f"dwarf-{i + 1}@localhost",
                "password": f"dwarf-{i + 1}",
                "full_name": f"Dwarf {i + 1}",
            },
            headers={"Authorization": "Bearer " + token},
        )
        # Если пользователь уже существует, то все OK
        assert ans.status_code in [200, 409]
        ans = requests.post(
            f"http://{AUTH_API_HOST}/v1/groups/{gid}/users/",
            json={"user_id": str(uid)},
            headers={"Authorization": "Bearer " + token},
        )
        assert ans.status_code == 200

    def teardown():
        """Удаляем тестовую группу, но входящие в нее пользователи не удаляются"""
        ans = requests.delete(
            f"http://{AUTH_API_HOST}/v1/groups/{gid}/",
            headers={"Authorization": "Bearer " + token},
        )
        assert ans.status_code == 200

    request.addfinalizer(teardown)
    return gid

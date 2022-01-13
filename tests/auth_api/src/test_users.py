import os
import pytest
import requests

AUTH_API_HOST = os.getenv('AUTH_API_HOST', 'flask_auth_api:5000')


def test_user_list():
    ans = requests.get(f"http://{AUTH_API_HOST}/v1/users/")
    assert ans.status_code == 200
    data = ans.json()
    assert isinstance(data, list)

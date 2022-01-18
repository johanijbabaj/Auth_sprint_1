import os

import pytest
import requests

AUTH_API_HOST = os.getenv("AUTH_API_HOST", "flask_auth_api:5000")


def test_user_list():
    ans = requests.get(f"http://{AUTH_API_HOST}/v1/users/")
    assert ans.status_code == 200
    data = ans.json()
    assert isinstance(data, list)


def test_admin_login():
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/users/login?login=admin&password={os.getenv('ADMIN_PASSWORD')}"
    )
    assert ans.status_code == 200
    data = ans.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_admin_history():
    """Просмотр администратором истории своих действий"""
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/users/login?login=admin&password={os.getenv('ADMIN_PASSWORD')}"
    )
    assert ans.status_code == 200
    data = ans.json()
    token = data["access_token"]
    ans = requests.get(
        f"http://{AUTH_API_HOST}/v1/users/history",
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 200
    data = ans.json()
    # В истории должна быть хотя бы одна запись - от того входа,
    # который был только что
    assert isinstance(data, list)
    assert len(data) >= 1


def test_nobody_history():
    """Просмотр пользователем без прав истории своих действий"""
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/users/login?login=nobody&password={os.getenv('NOBODY_PASSWORD')}"
    )
    assert ans.status_code == 200
    data = ans.json()
    token = data["access_token"]
    ans = requests.get(
        f"http://{AUTH_API_HOST}/v1/users/history",
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 200
    data = ans.json()
    # В истории должна быть хотя бы одна запись - от того входа,
    # который был только что
    assert isinstance(data, list)
    assert len(data) >= 1


def test_nobody_history_paginated():
    """Просмотр пользователем без прав истории своих действий постранично"""
    ans = requests.post(
        f"http://{AUTH_API_HOST}/v1/users/login?login=nobody&password={os.getenv('NOBODY_PASSWORD')}"
    )
    assert ans.status_code == 200
    data = ans.json()
    token = data["access_token"]
    ans = requests.get(
        f"http://{AUTH_API_HOST}/v1/users/history?page_size=5&page_number=1",
        headers={"Authorization": "Bearer " + token},
    )
    assert ans.status_code == 200
    data = ans.json()
    # В истории должна быть хотя бы одна запись - от того входа,
    # который был только что
    assert isinstance(data, list)
    assert len(data) >= 1

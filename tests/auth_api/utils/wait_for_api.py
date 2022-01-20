#! /usr/bin/env python

"""
Дождаться, пока будет доступен сервер auth_api по адресу
os.getenv('AUTH_API_HOST')
"""

import logging
import os
from time import sleep

import requests

API_HOST = os.getenv("AUTH_API_HOST")


def wait_for_auth_api(url: str = None, *, logger=None):
    """
    Дождаться пока по адресу url заработает сервер auth_api
    """
    url = url or f"http://{API_HOST}/test"
    while True:
        # Делаем пазузу для старта сервисов
        sleep(5)
        try:
            ans = requests.get(url)
        except requests.ConnectionError:
            if logger:
                logger.warning("Соединения с auth_api нет, попробуем позже")
            sleep(5)
            continue
        if ans.status_code != 200:
            if logger:
                logger.warning(
                    f"Ответ auth_api имеет код отличный от 200, попробуем позже"
                )
            sleep(5)
            continue
        if logger:
            logger.warning("Сервис auth_api готов к работе")
        return


if __name__ == "__main__":
    logger = logging.getLogger("default")
    logger.warning("Ждем готовности auth_api...")
    wait_for_auth_api(logger=logger)

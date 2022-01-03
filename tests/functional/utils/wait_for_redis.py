#! /usr/bin/env python

"""
Дождаться, пока будет доступен сервер Redis по адресу
os.getenv('REDIS_HOST', '127.0.0.1:6379)
"""

import logging
from time import sleep

import requests
from redis import Redis
from settings import TestSettings

redis_host = TestSettings().redis_host
redis_port = TestSettings().redis_port
redis_password = TestSettings().redis_password


def wait_for_redis(*, logger=None):
    """
    Дождаться пока заработает сервер redis
    """
    while True:
        try:
            rs = Redis(redis_host, port=redis_port, password=redis_password)
            ok = rs.ping()
        except requests.ConnectionError:
            if logger:
                logger.warning("Соединения с Redis нет, попробуем позже")
            sleep(5)
            continue
        if not ok:
            if logger:
                logger.warning("Ответ Redis не выглядит как надо, попробуем позже")
            sleep(5)
            continue
        if logger:
            logger.warning("Сервис Redis готов к работе")
        return


if __name__ == "__main__":
    logger = logging.getLogger("default")
    logger.warning("Ждем готовности Redis...")
    wait_for_redis(logger=logger)

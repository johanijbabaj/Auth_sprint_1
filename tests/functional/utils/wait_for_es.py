#! /usr/bin/env python

"""
Дождаться, пока будет доступен сервер ElasticSearch по адресу
os.getenv('ELASTIC_HOST', '127.0.0.1:9200)
"""

import logging
import os
from time import sleep

import requests

ELASTIC_HOST = os.getenv("ELASTIC_HOST")


def wait_for_es(url: str = None, *, logger=None):
    """
    Дождаться пока по адресу url заработает сервер ElasticSearch
    """
    url = url or f"http://{ELASTIC_HOST}"
    while True:
        try:
            ans = requests.get(url)
        except requests.ConnectionError:
            if logger:
                logger.warning("Соединения с Elastic нет, попробуем позже")
            sleep(5)
            continue
        if ans.status_code != 200:
            if logger:
                logger.warning("Ответ Elastic имеет код отличный от 200, попробуем позже")
            sleep(5)
            continue
        if ans.json().get('tagline').lower() != "you know, for search":
            if logger:
                logger.warning("Ответ Elastic не выглядит как надо, попробуем позже")
            sleep(5)
            continue
        if logger:
            logger.warning("Сервис ElasticSearch готов к работе")
        return


if __name__ == "__main__":
    logger = logging.getLogger("default")
    logger.warning("Ждем готовности ElasticSearch...")
    wait_for_es(logger=logger)

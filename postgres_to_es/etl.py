import logging
import time

from pg_to_es import PGtoES

logging_level = logging.DEBUG
main_logger = logging.getLogger()
main_logger.setLevel(logging_level)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging_level)
formatter = logging.Formatter("'%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

main_logger.addHandler(stream_handler)


def do_etl():
    main_logger.debug("Start loading from PostgreSQL to Elasticsearch")

    pte = PGtoES()
    while True:
        pte.sync()
        time.sleep(5)


if __name__ == '__main__':
    do_etl()

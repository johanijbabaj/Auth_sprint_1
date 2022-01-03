import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """
    Аналог orjson.dumps. Возвращает строку unicode а не bytes,
    так нужно для pydantic
    """
    return orjson.dumps(v, default=default).decode()


class OrjsonModel(BaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

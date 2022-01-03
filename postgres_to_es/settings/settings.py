from pydantic import BaseModel


class PostgresSettings(BaseModel):
    host: str
    port: int
    dbname: str
    password: str
    user: str


class ElasticsearchSettings(BaseModel):
    host: str
    port: int


class AllSettings(BaseModel):
    film_work_pg: PostgresSettings
    film_work_es: ElasticsearchSettings


class Settings:

    __settings = None

    def get_settings(self):
        if not self.__settings:
            self.__settings = AllSettings.parse_file('settings/settings.json')
        return self.__settings

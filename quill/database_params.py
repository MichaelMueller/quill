# builtin
from typing import Literal, Union
# 3rd party
from pydantic_settings import BaseSettings, SettingsConfigDict
# local
from quill.postgres_driver_params import PostgresDriverParams
from quill.sqlite_driver_params import SqliteDriverParams
from quill.mysql_driver_params import MysqlDriverParams

class DatabaseParams(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",            # optional: load from .env file
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        extra="ignore",             # ignore extra vars instead of raising
    )

    # define your settings
    driver:Union[SqliteDriverParams, PostgresDriverParams, MysqlDriverParams]

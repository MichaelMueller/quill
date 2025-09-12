# builtin
from typing import Literal
# 3rd party
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseParams(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",            # optional: load from .env file
        env_file_encoding="utf-8",
        extra="ignore",             # ignore extra vars instead of raising
    )

    # define your settings
    db_url: str
    driver:Literal["sqlite", "postgres"]

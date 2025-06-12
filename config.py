"""Модуль с настройками приложения."""

import sys
import logging
from logging import StreamHandler, Formatter
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(
    Formatter(
        fmt="[%(asctime)s: %(levelname)s] %(filename)s:%(funcName)s:%(lineno)d — %(message)s"
    )
)
logger.addHandler(handler)

# TODO: вынести логгер в отдельный файл
logger.debug("debug information")


class Settings(BaseSettings):
    """Настройки приложения."""

    base_dir: Path = Path(__file__).resolve().parent
    db_sqlite_path: Path = Path.joinpath(base_dir, "expenses.db")

    model_config = SettingsConfigDict(
        env_file=base_dir.parent / ".env", env_file_encoding="utf-8"
    )

    db_name: str = Field(default="expenses")

    tg_api_id: int = Field(default=12345678, description="Telegram API ID")
    tg_api_hash: str = Field(default="123qwe123qwe123", description="Telegram API HASH")
    tg_bot_token: str = Field(
        default="23423425234:aajdslfijsfij", description="Telegram BOT TOKEN"
    )

    db_url: str = Field(default="sqlite:///expenses.db")
    db_echo: bool = False

    @field_validator("db_echo", mode="before")
    @classmethod
    def parse_db_echo(cls, v: str | None) -> bool:
        if v is None:
            return False
        if isinstance(v, str):
            v = v.strip().lower()
            if v in ("true", "1", "yes", "on"):
                return True
            elif v in ("false", "0", "no", "off", ""):
                return False
        return bool(v)


settings = Settings()

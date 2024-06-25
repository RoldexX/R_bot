from __future__ import annotations

from dataclasses import dataclass
from environs import Env


@dataclass()
class TgBot:
    token: str


@dataclass()
class DatabaseConfig:
    database: str
    host: str
    port: int
    user: str
    password: str


@dataclass()
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None = None) -> Config:

    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
        ),
        db=DatabaseConfig(
            database=env('DATABASE'),
            host=env('DB_HOST'),
            port=env('DB_PORT'),
            user=env('DB_USER'),
            password=env('DB_PASSWORD'),
        )
    )

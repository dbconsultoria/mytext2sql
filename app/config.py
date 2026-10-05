"""Le configuracao do .env. Nenhuma outra parte do app deve ler os.environ diretamente."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    query_timeout_seconds: int
    max_rows: int

    ollama_url: str
    ollama_model: str
    ollama_timeout_seconds: int


def load_settings() -> Settings:
    return Settings(
        db_host=_get("DB_HOST", "localhost"),
        db_port=int(_get("DB_PORT", "3306")),
        db_name=_get("DB_NAME", "mydb"),
        db_user=_get("DB_USER", "texto_sql_ro"),
        db_password=_get("DB_PASSWORD", ""),
        query_timeout_seconds=int(_get("QUERY_TIMEOUT_SECONDS", "10")),
        max_rows=int(_get("MAX_ROWS", "1000")),
        ollama_url=_get("OLLAMA_URL", "http://localhost:11434"),
        ollama_model=_get("OLLAMA_MODEL", "qwen2.5-coder:7b"),
        ollama_timeout_seconds=int(_get("OLLAMA_TIMEOUT_SECONDS", "60")),
    )


settings = load_settings()

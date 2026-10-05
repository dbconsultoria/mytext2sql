"""Conexao somente leitura ao mydb. Timeout e limite de linhas por consulta."""
from __future__ import annotations

import time
from dataclasses import dataclass

import pandas as pd
import pymysql
import pymysql.cursors

from .config import settings


@dataclass
class QueryOutcome:
    df: pd.DataFrame
    elapsed_seconds: float
    truncated: bool


def get_connection() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        connect_timeout=5,
        read_timeout=settings.query_timeout_seconds + 5,
        write_timeout=5,
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
    )


def run_query(sql: str) -> QueryOutcome:
    """Executa um SELECT ja validado por sql_guard. Propaga pymysql.Error em caso de erro do banco."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # MySQL 8.0.4+: mata a consulta no servidor se passar do tempo limite.
            cursor.execute(f"SET SESSION MAX_EXECUTION_TIME = {settings.query_timeout_seconds * 1000}")

            start = time.monotonic()
            cursor.execute(sql)
            rows = cursor.fetchmany(settings.max_rows + 1)
            elapsed = time.monotonic() - start

            truncated = len(rows) > settings.max_rows
            rows = rows[: settings.max_rows]

            return QueryOutcome(df=pd.DataFrame(rows), elapsed_seconds=elapsed, truncated=truncated)
    finally:
        conn.close()

"""Pergunta -> SQL -> validacao -> execucao -> retry. No maximo 3 tentativas no total."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from .db import run_query
from .llm import ask_model
from .sql_guard import validate_sql

MAX_TENTATIVAS = 3


@dataclass
class PipelineResult:
    pergunta: str
    pode_responder: bool
    sql_final: Optional[str] = None
    explicacao: str = ""
    df: Optional[pd.DataFrame] = None
    tentativas: int = 0
    tempo_total_segundos: float = 0.0
    erros: list[str] = field(default_factory=list)
    motivo_recusa: Optional[str] = None
    truncado: bool = False


def executar_pipeline(pergunta: str, model: Optional[str] = None) -> PipelineResult:
    inicio = time.monotonic()
    erros: list[str] = []
    erro_anterior: Optional[str] = None

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        decisao = ask_model(pergunta, erro_anterior=erro_anterior, model=model)

        if not decisao.pode_responder:
            return PipelineResult(
                pergunta=pergunta,
                pode_responder=False,
                tentativas=tentativa,
                tempo_total_segundos=time.monotonic() - inicio,
                erros=erros,
                motivo_recusa=decisao.motivo or "O modelo nao conseguiu responder a essa pergunta.",
            )

        validacao = validate_sql(decisao.sql)
        if not validacao.ok:
            erro_fmt = f"Tentativa {tentativa}: SQL rejeitado pela validacao -> {validacao.error}"
            erros.append(erro_fmt)
            erro_anterior = (
                f"O SQL gerado foi rejeitado pela validacao: {validacao.error}\n"
                f"SQL gerado: {decisao.sql}"
            )
            continue

        try:
            outcome = run_query(validacao.sql)
        except Exception as exc:  # erro do banco (sintaxe, permissao, timeout, etc.)
            erro_fmt = f"Tentativa {tentativa}: erro do banco -> {exc}"
            erros.append(erro_fmt)
            erro_anterior = (
                f"O banco retornou um erro ao executar o SQL: {exc}\n"
                f"SQL gerado: {validacao.sql}"
            )
            continue

        return PipelineResult(
            pergunta=pergunta,
            pode_responder=True,
            sql_final=validacao.sql,
            explicacao=decisao.explicacao,
            df=outcome.df,
            tentativas=tentativa,
            tempo_total_segundos=time.monotonic() - inicio,
            erros=erros,
            truncado=outcome.truncated,
        )

    return PipelineResult(
        pergunta=pergunta,
        pode_responder=False,
        tentativas=MAX_TENTATIVAS,
        tempo_total_segundos=time.monotonic() - inicio,
        erros=erros,
        motivo_recusa=f"Nao foi possivel gerar uma consulta valida apos {MAX_TENTATIVAS} tentativas.",
    )

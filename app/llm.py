"""Cliente do Ollama: chat com saida estruturada (JSON schema), temperature 0."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Optional

import ollama

from .config import settings
from .prompts import build_messages
from .schema_context import JSON_SCHEMA

logger = logging.getLogger("text2sql.llm")

# Contexto fixo (system prompt + 10 exemplos few-shot) mede ~2.1k-2.5k tokens
# (chars_totais / 4 a / 3.5, ver app/prompts.py). Com a pergunta do usuario,
# o erro de uma retentativa e a resposta do modelo, 8192 da bastante folga
# sem desperdicar memoria à toa.
NUM_CTX = 8192


@dataclass
class ModelDecision:
    pode_responder: bool
    sql: str
    explicacao: str
    motivo: str
    raw_response: str


def _client() -> ollama.Client:
    return ollama.Client(host=settings.ollama_url, timeout=settings.ollama_timeout_seconds)


def ask_model(pergunta: str, erro_anterior: Optional[str] = None, model: Optional[str] = None) -> ModelDecision:
    model = model or settings.ollama_model
    messages = build_messages(pergunta, erro_anterior=erro_anterior)

    logger.debug("Ollama request | model=%s | pergunta=%r | erro_anterior=%r",
                 model, pergunta, erro_anterior)

    response = _client().chat(
        model=model,
        messages=messages,
        format=JSON_SCHEMA,
        options={"temperature": 0, "num_ctx": NUM_CTX},
    )

    content = response["message"]["content"]
    logger.debug("Ollama response | content=%r", content)

    return _parse_decision(content)


def _parse_decision(content: str) -> ModelDecision:
    data = _extract_json(content)

    return ModelDecision(
        pode_responder=bool(data.get("pode_responder", False)),
        sql=_extract_sql(data.get("sql", "")),
        explicacao=str(data.get("explicacao", "")),
        motivo=str(data.get("motivo", "")),
        raw_response=content,
    )


def _extract_json(content: str) -> dict:
    """Parser tolerante: tenta JSON direto; se nao der, procura o maior
    bloco {...} no texto (cobre respostas com texto/markdown ao redor)."""
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    brace_match = re.search(r"\{.*\}", content, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    logger.warning("Nao foi possivel extrair JSON da resposta do modelo: %r", content)
    return {
        "pode_responder": False,
        "sql": "",
        "explicacao": "",
        "motivo": "O modelo nao retornou um JSON valido.",
    }


def _extract_sql(sql_field: str) -> str:
    """Se o modelo colocar o SQL dentro de um bloco markdown mesmo dentro do
    campo JSON, extrai so o SQL."""
    sql_field = sql_field.strip()
    fenced = re.search(r"```(?:sql)?\s*(.*?)\s*```", sql_field, re.DOTALL)
    if fenced:
        return fenced.group(1).strip()
    return sql_field

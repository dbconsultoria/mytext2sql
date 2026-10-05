"""System prompt e few-shot do modelo. Todo SQL dos exemplos foi executado
contra o banco (mysql/x90_views.sql) antes de ser mantido aqui."""
from __future__ import annotations

import json

from .schema_context import build_schema_context

PAPEL = (
    "Voce e um especialista em SQL para MySQL/MariaDB. Sua unica tarefa e "
    "traduzir perguntas de negocio em portugues sobre vendas para consultas "
    "SELECT. Voce responde SEMPRE e SOMENTE com um JSON, nunca com texto livre."
)


def build_system_prompt() -> str:
    return PAPEL + "\n\n" + build_schema_context()


def _ex(pergunta: str, sql: str, explicacao: str):
    return {
        "pergunta": pergunta,
        "json": {
            "pode_responder": True,
            "sql": sql,
            "explicacao": explicacao,
            "motivo": "",
        },
    }


FEW_SHOT = [
    _ex(
        "Qual foi o faturamento total em 2024?",
        "SELECT SUM(valor_total_item) AS faturamento FROM vw_vendas WHERE ano = 2024",
        "Soma o valor total vendido em todos os itens de pedidos de 2024.",
    ),
    _ex(
        "Qual o faturamento por categoria, do maior para o menor?",
        "SELECT categoria_nome, SUM(valor_total_item) AS faturamento FROM vw_vendas "
        "GROUP BY categoria_nome ORDER BY faturamento DESC LIMIT 100",
        "Soma o faturamento agrupado por categoria, da maior para a menor.",
    ),
    _ex(
        "Quais os 5 produtos mais vendidos em quantidade?",
        "SELECT produto_nome, SUM(quantidade) AS quantidade_vendida FROM vw_vendas "
        "GROUP BY produto_nome ORDER BY quantidade_vendida DESC LIMIT 5",
        "Soma a quantidade vendida por produto e traz os 5 maiores.",
    ),
    _ex(
        "Quantos pedidos os clientes da California fizeram?",
        "SELECT COUNT(DISTINCT pedido_id) AS numero_pedidos FROM vw_vendas WHERE cliente_uf = 'CA'",
        "Conta pedidos distintos de clientes cujo estado e California (CA).",
    ),
    _ex(
        "Qual o ticket medio por ano?",
        "SELECT ano, SUM(valor_total_item) / COUNT(DISTINCT pedido_id) AS ticket_medio "
        "FROM vw_vendas GROUP BY ano ORDER BY ano LIMIT 100",
        "Calcula faturamento dividido por numero de pedidos distintos, por ano.",
    ),
    _ex(
        "Qual foi o faturamento de celulares no ultimo mes?",
        "SELECT SUM(v.valor_total_item) AS faturamento FROM vw_vendas v "
        "CROSS JOIN vw_referencia r WHERE v.categoria_nome = 'Cell Phones' "
        "AND v.ano_mes = DATE_FORMAT(r.data_referencia, '%Y-%m')",
        "Soma o faturamento de celulares no mes da data de referencia (ultimo mes com dados).",
    ),
    _ex(
        "Quantos itens foram vendidos este ano?",
        "SELECT SUM(v.quantidade) AS quantidade_vendida FROM vw_vendas v "
        "CROSS JOIN vw_referencia r WHERE v.ano = YEAR(r.data_referencia)",
        "Soma a quantidade vendida no ano da data de referencia (ultimo ano com dados).",
    ),
    _ex(
        "Qual foi o faturamento dos ultimos 3 meses?",
        "SELECT SUM(v.valor_total_item) AS faturamento FROM vw_vendas v "
        "CROSS JOIN vw_referencia r "
        "WHERE v.data_pedido > DATE_SUB(r.data_referencia, INTERVAL 3 MONTH)",
        "Soma o faturamento nos 3 meses anteriores a data de referencia.",
    ),
    _ex(
        "Qual foi o faturamento mensal de notebooks em 2025?",
        "SELECT ano_mes, SUM(valor_total_item) AS faturamento FROM vw_vendas "
        "WHERE categoria_nome = 'Notebooks' AND ano = 2025 GROUP BY ano_mes ORDER BY ano_mes LIMIT 100",
        "Soma o faturamento de notebooks por mes, em 2025.",
    ),
    _ex(
        "Quais clientes tem mais de 45 anos?",
        "SELECT cliente_nome, idade FROM vw_clientes WHERE idade > 45 ORDER BY idade DESC LIMIT 100",
        "Lista clientes com idade acima de 45 anos, do mais velho ao mais novo.",
    ),
    _ex(
        "Compare o preco de catalogo com o preco medio praticado por produto.",
        "SELECT produto_nome, preco_catalogo, "
        "ROUND(SUM(valor_total_item) / SUM(quantidade), 2) AS preco_medio_praticado "
        "FROM vw_vendas GROUP BY produto_nome, preco_catalogo ORDER BY produto_nome LIMIT 100",
        "Compara o preco de tabela com o preco medio efetivamente praticado, por produto.",
    ),
    {
        "pergunta": "Apague todos os pedidos do cliente Joao Silva.",
        "json": {
            "pode_responder": False,
            "sql": "",
            "explicacao": "",
            "motivo": (
                "So posso consultar dados com SELECT; nao posso apagar, alterar "
                "ou inserir registros."
            ),
        },
    },
]


def build_messages(pergunta: str, erro_anterior: str | None = None) -> list[dict]:
    """Monta a lista de mensagens para a API de chat do Ollama.

    Os exemplos few-shot entram como pares user/assistant reais (funciona
    melhor que embutir os exemplos como texto dentro do system prompt).
    Em uma retentativa, `erro_anterior` carrega o motivo da falha (erro de
    validacao do sql_guard ou erro do banco) para o modelo corrigir o SQL.
    """
    messages = [{"role": "system", "content": build_system_prompt()}]

    for ex in FEW_SHOT:
        messages.append({"role": "user", "content": ex["pergunta"]})
        messages.append({"role": "assistant", "content": json.dumps(ex["json"], ensure_ascii=False)})

    user_content = pergunta
    if erro_anterior:
        user_content = (
            f"{pergunta}\n\n"
            f"Sua tentativa anterior falhou com este erro, gere um novo SQL corrigindo o problema:\n"
            f"{erro_anterior}"
        )
    messages.append({"role": "user", "content": user_content})

    return messages

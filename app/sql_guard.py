"""Validacao do SQL gerado pelo modelo antes de executar no banco.

Duas camadas de seguranca: isso aqui (validacao sintatica/semantica do SQL)
e o usuario `texto_sql_ro`, que so tem GRANT SELECT nas views (sql_guard nao
substitui permissoes de banco, e vice-versa).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import sqlglot
from sqlglot import exp

DIALECT = "mysql"

ALLOWED_VIEWS = {"vw_vendas", "vw_clientes", "vw_produtos", "vw_referencia"}

FORBIDDEN_FUNCTIONS = {
    "SLEEP",
    "BENCHMARK",
    "LOAD_FILE",
    "GET_LOCK",
    "RELEASE_LOCK",
    "SYS_EXEC",
    "SYS_EVAL",
}

DEFAULT_LIMIT = 100

# Comentario versionado do MySQL (`/*! ... */`): o SERVIDOR executa o
# conteudo como SQL de verdade. sqlglot trata isso como comentario inerte,
# entao a AST pareceria "segura" mesmo escondendo um comando real.
VERSIONED_COMMENT_RE = re.compile(r"/\*!")

_AGGREGATE_TYPES = (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)


@dataclass
class ValidationResult:
    ok: bool
    sql: Optional[str] = None
    error: Optional[str] = None


def validate_sql(raw_sql: str) -> ValidationResult:
    """Valida e, se preciso, reescreve o SQL (ex.: injeta LIMIT).

    O SQL devolvido em `.sql` e sempre reserializado a partir da AST
    (nunca a string original), o que por si so descarta qualquer
    comentario/truque escondido no texto bruto.
    """
    sql_text = raw_sql.strip()
    if not sql_text:
        return ValidationResult(False, error="SQL vazio.")

    if VERSIONED_COMMENT_RE.search(sql_text):
        return ValidationResult(
            False,
            error=(
                "Comentario versionado do MySQL ('/*!...*/') nao e permitido: "
                "o servidor executa esse conteudo como SQL real."
            ),
        )

    try:
        statements = [s for s in sqlglot.parse(sql_text, read=DIALECT) if s is not None]
    except Exception as exc:
        return ValidationResult(False, error=f"SQL invalido, nao foi possivel interpretar: {exc}")

    if len(statements) != 1:
        return ValidationResult(
            False,
            error=(
                f"Envie exatamente um comando SELECT. "
                f"Foram encontrados {len(statements)} comandos."
            ),
        )

    root = statements[0]

    if not isinstance(root, (exp.Select, exp.Union)):
        return ValidationResult(
            False,
            error=(
                f"Apenas comandos SELECT sao permitidos "
                f"(incluindo WITH ... SELECT). Recebido: {type(root).__name__}."
            ),
        )

    for select in root.find_all(exp.Select):
        if select.args.get("into") is not None:
            return ValidationResult(False, error="SELECT ... INTO nao e permitido.")

    cte_names = {
        cte.alias.lower()
        for with_clause in root.find_all(exp.With)
        for cte in with_clause.expressions
        if cte.alias
    }

    for table in root.find_all(exp.Table):
        name = table.name.lower()
        if name in cte_names:
            continue
        if name not in ALLOWED_VIEWS:
            return ValidationResult(
                False,
                error=(
                    f"Tabela/view '{table.name}' nao e permitida. "
                    f"Use apenas: {', '.join(sorted(ALLOWED_VIEWS))}."
                ),
            )

    for func in root.find_all(exp.Func):
        fname = (func.name if isinstance(func, exp.Anonymous) else func.sql_name()) or ""
        if fname.upper() in FORBIDDEN_FUNCTIONS:
            return ValidationResult(False, error=f"Funcao '{fname.upper()}' nao e permitida.")

    root = _ensure_limit(root)

    return ValidationResult(True, sql=root.sql(dialect=DIALECT, comments=False))


def _ensure_limit(root):
    if root.args.get("limit") is not None:
        return root
    if isinstance(root, exp.Select) and _is_single_row_aggregate(root):
        return root
    return root.limit(DEFAULT_LIMIT)


def _is_single_row_aggregate(select: exp.Select) -> bool:
    if select.args.get("group"):
        return False
    if not select.expressions:
        return False
    for proj in select.expressions:
        inner = proj.this if isinstance(proj, exp.Alias) else proj
        if not _only_aggregates_and_literals(inner):
            return False
    return True


def _only_aggregates_and_literals(node) -> bool:
    if isinstance(node, _AGGREGATE_TYPES) or isinstance(node, exp.Literal):
        return True
    if isinstance(node, (exp.Binary, exp.Paren, exp.Neg)):
        children = [v for v in node.args.values() if isinstance(v, exp.Expression)]
        return bool(children) and all(_only_aggregates_and_literals(c) for c in children)
    return False

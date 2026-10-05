"""Roda o pipeline contra eval/perguntas.yaml e compara o RESULTADO da
execucao (nao o texto do SQL) com o gabarito. Gera relatorio no terminal e em CSV.

Uso:
    python eval/run_eval.py
    python eval/run_eval.py --model qwen2.5-coder:7b
    python eval/run_eval.py --model llama3.1:8b --saida eval/relatorio_llama.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.db import run_query  # noqa: E402
from app.pipeline import executar_pipeline  # noqa: E402

NUMERIC_TYPES = (int, float, Decimal)


def carregar_perguntas(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _normalize_value(v):
    if v is None:
        return None
    if isinstance(v, NUMERIC_TYPES) and not isinstance(v, bool):
        return round(float(v), 2)  # tolerancia de 0.01 em valores decimais
    return str(v).strip()


def _normalize_df(df) -> list[tuple]:
    return [tuple(_normalize_value(v) for v in row) for row in df.itertuples(index=False, name=None)]


def comparar_resultados(df_model, df_gabarito, sql_gabarito: str) -> tuple[bool, str]:
    if df_model is None:
        return False, "pipeline nao retornou dados"

    if df_model.shape[1] != df_gabarito.shape[1]:
        return False, (
            f"numero de colunas diferente (modelo={df_model.shape[1]}, "
            f"gabarito={df_gabarito.shape[1]})"
        )

    linhas_model = _normalize_df(df_model)
    linhas_gabarito = _normalize_df(df_gabarito)

    tem_order_by = "order by" in sql_gabarito.lower()
    if tem_order_by:
        iguais = linhas_model == linhas_gabarito
    else:
        iguais = Counter(linhas_model) == Counter(linhas_gabarito)

    if not iguais:
        return False, (
            f"linhas diferentes (modelo={len(linhas_model)} linhas, "
            f"gabarito={len(linhas_gabarito)} linhas)"
        )
    return True, ""


def avaliar(model: str | None, perguntas_path: str) -> list[dict]:
    perguntas = carregar_perguntas(perguntas_path)
    linhas_relatorio = []

    for item in perguntas:
        pergunta = item["pergunta"]
        sql_gabarito = item.get("sql_gabarito")
        e_recusa = sql_gabarito is None

        resultado = executar_pipeline(pergunta, model=model)

        if e_recusa:
            acertou = not resultado.pode_responder
            detalhe = "" if acertou else "deveria ter recusado e nao recusou"
        elif not resultado.pode_responder:
            acertou = False
            detalhe = f"pipeline recusou: {resultado.motivo_recusa}"
        else:
            try:
                gab_outcome = run_query(sql_gabarito)
            except Exception as exc:
                acertou = False
                detalhe = f"erro ao rodar SQL gabarito: {exc}"
            else:
                acertou, detalhe = comparar_resultados(resultado.df, gab_outcome.df, sql_gabarito)

        linhas_relatorio.append(
            {
                "pergunta": pergunta,
                "nivel": item["nivel"],
                "tags": ";".join(item["tags"]),
                "acertou": acertou,
                "detalhe": detalhe,
                "tentativas": resultado.tentativas,
                "tempo_segundos": round(resultado.tempo_total_segundos, 3),
            }
        )

    return linhas_relatorio


def _percentual(acertos: int, total: int) -> str:
    return f"{100 * acertos / total:.1f}%" if total else "n/a"


def imprimir_relatorio(linhas: list[dict], model: str) -> None:
    total = len(linhas)
    acertos = sum(1 for l in linhas if l["acertou"])

    print(f"Modelo: {model}")
    print(f"Acuracia geral: {acertos}/{total} ({_percentual(acertos, total)})")

    print("\nPor nivel:")
    for nivel in ["facil", "medio", "dificil"]:
        subset = [l for l in linhas if l["nivel"] == nivel]
        if not subset:
            continue
        ac = sum(1 for l in subset if l["acertou"])
        print(f"  {nivel:8s}: {ac}/{len(subset)} ({_percentual(ac, len(subset))})")

    print("\nPor tag:")
    tags_vistas = sorted({t for l in linhas for t in l["tags"].split(";")})
    for tag in tags_vistas:
        subset = [l for l in linhas if tag in l["tags"].split(";")]
        ac = sum(1 for l in subset if l["acertou"])
        print(f"  {tag:20s}: {ac}/{len(subset)} ({_percentual(ac, len(subset))})")

    media_tentativas = sum(l["tentativas"] for l in linhas) / total
    media_tempo = sum(l["tempo_segundos"] for l in linhas) / total
    print(f"\nMedia de tentativas: {media_tentativas:.2f}")
    print(f"Tempo medio por pergunta: {media_tempo:.2f}s")

    falhas = [l for l in linhas if not l["acertou"]]
    if falhas:
        print(f"\nFalhas ({len(falhas)}):")
        for l in falhas:
            print(f"  [{l['nivel']}] {l['pergunta']!r} -> {l['detalhe']}")


def salvar_csv(linhas: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["pergunta", "nivel", "tags", "acertou", "detalhe", "tentativas", "tempo_segundos"],
        )
        writer.writeheader()
        writer.writerows(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia o pipeline text2sql.")
    parser.add_argument("--model", default=None, help="Modelo do Ollama (default: OLLAMA_MODEL do .env)")
    parser.add_argument(
        "--perguntas",
        default=str(Path(__file__).parent / "perguntas.yaml"),
        help="Caminho do YAML de perguntas",
    )
    parser.add_argument("--saida", default=None, help="Caminho do CSV de saida")
    args = parser.parse_args()

    model = args.model or settings.ollama_model
    linhas = avaliar(model=args.model, perguntas_path=args.perguntas)
    imprimir_relatorio(linhas, model)

    saida = args.saida or str(Path(__file__).parent / f"relatorio_{model.replace(':', '_')}.csv")
    salvar_csv(linhas, saida)
    print(f"\nRelatorio salvo em {saida}")


if __name__ == "__main__":
    main()

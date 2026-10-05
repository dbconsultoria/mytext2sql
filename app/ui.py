"""Interface Streamlit: pergunta em portugues -> SQL -> tabela -> grafico automatico."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# streamlit executa este arquivo como script avulso (__main__), nao como parte
# do pacote `app` - por isso precisa da raiz do projeto no sys.path para os
# imports absolutos funcionarem, em vez de imports relativos (quebram aqui).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.pipeline import executar_pipeline  # noqa: E402

TIME_COLS = {"ano", "mes", "ano_mes"}

st.set_page_config(page_title="Text2SQL - Vendas", page_icon="📊", layout="wide")

if "historico" not in st.session_state:
    st.session_state["historico"] = []

with st.sidebar:
    st.subheader("Modelo em uso")
    st.code(settings.ollama_model, language=None)
    st.caption(settings.ollama_url)

    st.subheader("Historico da sessao")
    if not st.session_state["historico"]:
        st.caption("Nenhuma pergunta ainda.")
    for item in reversed(st.session_state["historico"]):
        icone = "✅" if item["pode_responder"] else "🚫"
        st.markdown(f"{icone} {item['pergunta']}")


def _tentar_grafico(df: pd.DataFrame) -> None:
    if df is None or df.empty or len(df) < 2:
        return

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        return

    time_cols = [c for c in df.columns if c in TIME_COLS]
    if time_cols:
        eixo_x, metrica = time_cols[0], numeric_cols[0]
        st.line_chart(df.set_index(eixo_x)[[metrica]])
        return

    categoricas = [c for c in df.columns if c not in numeric_cols]
    if categoricas and len(df) <= 50:
        eixo_x, metrica = categoricas[0], numeric_cols[0]
        st.bar_chart(df.set_index(eixo_x)[[metrica]])


st.title("Text2SQL - Vendas")
st.caption("Faca uma pergunta em portugues sobre vendas, clientes ou produtos.")

pergunta = st.text_area("Sua pergunta", placeholder="Ex.: qual foi o faturamento por categoria em 2024?")
perguntar = st.button("Perguntar", type="primary")

if perguntar and pergunta.strip():
    with st.spinner("Gerando e executando a consulta..."):
        resultado = executar_pipeline(pergunta.strip())

    st.session_state["historico"].append(
        {"pergunta": pergunta.strip(), "pode_responder": resultado.pode_responder}
    )

    if not resultado.pode_responder:
        st.warning(resultado.motivo_recusa or "Nao foi possivel responder a essa pergunta.")
    else:
        if resultado.explicacao:
            st.markdown(f"**{resultado.explicacao}**")

        with st.expander("SQL gerado", expanded=False):
            st.code(resultado.sql_final, language="sql")

        st.dataframe(resultado.df, width="stretch")
        if resultado.truncado:
            st.caption(f"Resultado truncado em {settings.max_rows} linhas.")

        _tentar_grafico(resultado.df)

    with st.expander("Detalhes da execucao"):
        st.write(f"Tentativas: {resultado.tentativas}")
        st.write(f"Tempo total: {resultado.tempo_total_segundos:.2f}s")
        if resultado.erros:
            st.write("Erros intermediarios:")
            for erro in resultado.erros:
                st.write(f"- {erro}")
elif perguntar:
    st.info("Digite uma pergunta antes de clicar em Perguntar.")

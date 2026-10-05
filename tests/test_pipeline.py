import pandas as pd

from app.llm import ModelDecision
from app.pipeline import executar_pipeline
from app.db import QueryOutcome


def _decisao(pode_responder=True, sql="", explicacao="", motivo=""):
    return ModelDecision(
        pode_responder=pode_responder,
        sql=sql,
        explicacao=explicacao,
        motivo=motivo,
        raw_response="",
    )


def test_recusa_do_modelo_nao_tenta_de_novo(monkeypatch):
    chamadas = []

    def fake_ask_model(pergunta, erro_anterior=None, model=None):
        chamadas.append(pergunta)
        return _decisao(pode_responder=False, motivo="Isso apagaria dados.")

    monkeypatch.setattr("app.pipeline.ask_model", fake_ask_model)

    r = executar_pipeline("apague tudo")

    assert not r.pode_responder
    assert r.motivo_recusa == "Isso apagaria dados."
    assert r.tentativas == 1
    assert len(chamadas) == 1


def test_sql_invalido_tenta_de_novo_e_depois_funciona(monkeypatch):
    respostas = [
        _decisao(sql="SELECT * FROM tbcustomers"),  # tabela proibida
        _decisao(sql="SELECT COUNT(*) AS n FROM vw_vendas", explicacao="conta linhas"),
    ]

    def fake_ask_model(pergunta, erro_anterior=None, model=None):
        return respostas.pop(0)

    def fake_run_query(sql):
        return QueryOutcome(df=pd.DataFrame({"n": [6720]}), elapsed_seconds=0.01, truncated=False)

    monkeypatch.setattr("app.pipeline.ask_model", fake_ask_model)
    monkeypatch.setattr("app.pipeline.run_query", fake_run_query)

    r = executar_pipeline("quantas linhas tem?")

    assert r.pode_responder
    assert r.tentativas == 2
    assert len(r.erros) == 1
    assert "nao e permitida" in r.erros[0]
    assert r.df.iloc[0]["n"] == 6720


def test_tres_sqls_invalidos_esgota_tentativas(monkeypatch):
    def fake_ask_model(pergunta, erro_anterior=None, model=None):
        return _decisao(sql="SELECT * FROM tbcustomers")

    monkeypatch.setattr("app.pipeline.ask_model", fake_ask_model)

    r = executar_pipeline("quem comprou mais?")

    assert not r.pode_responder
    assert r.tentativas == 3
    assert len(r.erros) == 3


def test_erro_do_banco_tenta_de_novo_e_depois_funciona(monkeypatch):
    def fake_ask_model(pergunta, erro_anterior=None, model=None):
        return _decisao(sql="SELECT SUM(valor_total_item) AS faturamento FROM vw_vendas")

    chamadas_db = {"n": 0}

    def fake_run_query(sql):
        chamadas_db["n"] += 1
        if chamadas_db["n"] == 1:
            raise RuntimeError("Unknown column 'xyz'")
        return QueryOutcome(df=pd.DataFrame({"faturamento": [100.0]}), elapsed_seconds=0.01, truncated=False)

    monkeypatch.setattr("app.pipeline.ask_model", fake_ask_model)
    monkeypatch.setattr("app.pipeline.run_query", fake_run_query)

    r = executar_pipeline("qual o faturamento?")

    assert r.pode_responder
    assert r.tentativas == 2
    assert len(r.erros) == 1
    assert "erro do banco" in r.erros[0]

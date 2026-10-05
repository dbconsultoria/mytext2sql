from app.sql_guard import validate_sql


# --- casos validos -----------------------------------------------------

def test_select_simples_com_limit_mantido():
    r = validate_sql("SELECT cliente_nome FROM vw_clientes LIMIT 10")
    assert r.ok
    assert "LIMIT 10" in r.sql


def test_listagem_sem_limit_recebe_limit_padrao():
    r = validate_sql("SELECT produto_nome FROM vw_produtos")
    assert r.ok
    assert "LIMIT 100" in r.sql


def test_agregacao_de_uma_linha_nao_recebe_limit():
    r = validate_sql("SELECT SUM(valor_total_item) AS faturamento FROM vw_vendas")
    assert r.ok
    assert "LIMIT" not in r.sql


def test_ticket_medio_expressao_so_com_agregacoes_nao_recebe_limit():
    sql = (
        "SELECT SUM(valor_total_item) / COUNT(DISTINCT pedido_id) AS ticket_medio "
        "FROM vw_vendas"
    )
    r = validate_sql(sql)
    assert r.ok
    assert "LIMIT" not in r.sql


def test_group_by_e_tratado_como_listagem_e_recebe_limit():
    sql = "SELECT categoria_nome, SUM(valor_total_item) AS faturamento FROM vw_vendas GROUP BY categoria_nome"
    r = validate_sql(sql)
    assert r.ok
    assert "LIMIT 100" in r.sql


def test_cte_com_view_permitida_e_aceita():
    sql = (
        "WITH base AS (SELECT categoria_nome, valor_total_item FROM vw_vendas) "
        "SELECT categoria_nome, SUM(valor_total_item) FROM base GROUP BY categoria_nome"
    )
    r = validate_sql(sql)
    assert r.ok


def test_like_em_nome_e_aceito():
    r = validate_sql("SELECT cliente_nome FROM vw_clientes WHERE cliente_nome LIKE '%Smith%'")
    assert r.ok


# --- casos maliciosos / invalidos ---------------------------------------

def test_sql_vazio_e_rejeitado():
    r = validate_sql("")
    assert not r.ok


def test_multiplos_comandos_sao_rejeitados():
    r = validate_sql("SELECT 1 FROM vw_vendas; SELECT 2 FROM vw_vendas")
    assert not r.ok
    assert "um comando SELECT" in r.error


def test_drop_table_e_rejeitado():
    r = validate_sql("DROP TABLE vw_vendas")
    assert not r.ok


def test_insert_e_rejeitado():
    r = validate_sql("INSERT INTO vw_vendas (pedido_id) VALUES (1)")
    assert not r.ok


def test_update_e_rejeitado():
    r = validate_sql("UPDATE vw_vendas SET quantidade = 0")
    assert not r.ok


def test_delete_e_rejeitado():
    r = validate_sql("DELETE FROM vw_vendas")
    assert not r.ok


def test_tabela_crua_fora_da_whitelist_e_rejeitada():
    r = validate_sql("SELECT * FROM tbcustomers")
    assert not r.ok
    assert "nao e permitida" in r.error


def test_information_schema_e_rejeitado():
    r = validate_sql("SELECT table_name FROM information_schema.tables")
    assert not r.ok


def test_sleep_e_rejeitado():
    r = validate_sql("SELECT SLEEP(5)")
    assert not r.ok
    assert "SLEEP" in r.error


def test_benchmark_e_rejeitado():
    r = validate_sql("SELECT BENCHMARK(1000000, MD5('x'))")
    assert not r.ok


def test_load_file_e_rejeitado():
    r = validate_sql("SELECT LOAD_FILE('/etc/passwd')")
    assert not r.ok


def test_into_outfile_e_rejeitado():
    r = validate_sql("SELECT * FROM vw_vendas INTO OUTFILE '/tmp/x.csv'")
    assert not r.ok


def test_comentario_versionado_e_rejeitado():
    r = validate_sql("SELECT /*!50000DROP*/ * FROM vw_vendas")
    assert not r.ok
    assert "versionado" in r.error


def test_comentario_de_linha_com_comando_e_inofensivo_mas_tabela_ainda_valida():
    # sqlglot descarta comentarios de linha; o SQL resultante e reserializado
    # a partir da AST, entao o comentario nunca chega ao banco.
    r = validate_sql("SELECT * FROM vw_vendas -- ; DROP TABLE x")
    assert r.ok
    assert "DROP" not in r.sql.upper()


def test_grant_e_rejeitado():
    r = validate_sql("GRANT SELECT ON mydb.vw_vendas TO 'x'@'%'")
    assert not r.ok

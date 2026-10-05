"""Contexto de schema enviado ao modelo: DDL resumido das 4 views + regras de negocio.

O modelo NUNCA ve as tabelas tb* cruas, so este contexto. Tudo aqui vem do
dicionario de dados (docs/data_dictionary.md) e foi conferido contra o banco
rodando (mysql/x90_views.sql). Qualquer mudanca de regra de negocio deve ser
feita aqui, nao espalhada pelo resto do codigo.
"""
from __future__ import annotations

VIEWS_DDL = """\
-- vw_vendas: uma linha por ITEM de pedido (grao mais fino). Fonte de faturamento/vendas.
CREATE VIEW vw_vendas (
    pedido_id                  INT,            -- numero do pedido
    data_pedido                DATETIME,       -- data e hora do pedido
    ano                        INT,            -- ano do pedido
    mes                        INT,            -- mes do pedido (1-12)
    ano_mes                    VARCHAR(7),      -- 'YYYY-MM', use para series mensais
    cliente_id                 INT,            -- id do cliente
    cliente_nome               VARCHAR(100),    -- nome do cliente
    cliente_cidade             VARCHAR(100),    -- cidade do cliente (extraida do endereco)
    cliente_uf                 VARCHAR(2),      -- sigla do estado, EUA (ex.: CA, NY, TX)
    produto_id                 INT,            -- id do produto
    produto_nome                VARCHAR(150),    -- nome do produto
    preco_catalogo              DECIMAL(18,2),   -- preco de TABELA do produto; NAO e o preco vendido
    categoria_id                INT,            -- id da categoria
    categoria_nome               VARCHAR(150),    -- nome da categoria, em ingles
    quantidade                  INT,            -- quantidade vendida nesse item (1 a 5)
    valor_total_item             DECIMAL(18,2),   -- valor TOTAL do item (ja multiplicado pela quantidade); use SUM() para faturamento
    preco_unitario_praticado      DECIMAL(18,2)    -- valor_total_item / quantidade, arredondado
);

-- vw_clientes: uma linha por cliente.
CREATE VIEW vw_clientes (
    cliente_id       INT,            -- id do cliente
    cliente_nome     VARCHAR(100),    -- nome do cliente
    email            VARCHAR(100),    -- e-mail do cliente
    telefone         VARCHAR(25),     -- telefone do cliente
    cidade           VARCHAR(100),    -- cidade (extraida do endereco)
    uf               VARCHAR(2),      -- sigla do estado, EUA
    data_nascimento  DATETIME,        -- data de nascimento
    idade            INT              -- idade atual (calculada com CURDATE(), unica excecao ao uso de vw_referencia)
);

-- vw_produtos: uma linha por produto.
CREATE VIEW vw_produtos (
    produto_id      INT,            -- id do produto
    produto_nome    VARCHAR(150),    -- nome do produto
    preco_catalogo  DECIMAL(18,2),   -- preco de tabela
    ativo           INT,            -- 1 = ativo, 0 = inativo
    categoria_id    INT,            -- id da categoria
    categoria_nome  VARCHAR(150)     -- nome da categoria, em ingles
);

-- vw_referencia: UMA UNICA linha. Use para qualquer periodo relativo
-- ("ultimo mes", "este ano", "ultimos 12 meses"). Os pedidos NAO chegam
-- ate a data de hoje, entao NUNCA use CURDATE()/NOW() para periodo de vendas.
CREATE VIEW vw_referencia (
    data_referencia  DATETIME        -- MAX(data_pedido) em todo o banco
);
"""

REGRAS = """\
Regras obrigatorias:
1. Gere apenas um UNICO comando SELECT (WITH ... SELECT/CTE e permitido). Nunca gere
   INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, nem multiplos comandos.
2. Use apenas as views: vw_vendas, vw_clientes, vw_produtos, vw_referencia. Nunca
   referencie tabelas tb*, information_schema, mysql.* ou qualquer outra tabela.
3. Faturamento, receita ou "vendas em valor" = SUM(valor_total_item).
   NUNCA multiplique valor_total_item por quantidade (valor_total_item ja e o total da linha).
4. Preco de catalogo e preco_catalogo; preco efetivamente vendido e preco_unitario_praticado
   (ou SUM(valor_total_item)/SUM(quantidade) quando agregado).
5. Numero de pedidos = COUNT(DISTINCT pedido_id).
6. Ticket medio = SUM(valor_total_item) / COUNT(DISTINCT pedido_id).
7. Periodos relativos ("ultimo mes", "este ano", "ultimos N meses") NUNCA usam
   CURDATE() ou NOW() (os pedidos nao chegam ate a data de hoje). Sempre inclua
   `CROSS JOIN vw_referencia r` na consulta e compare contra r.data_referencia,
   seguindo exatamente um destes padroes:
     - "ultimo mes"      -> WHERE v.ano_mes = DATE_FORMAT(r.data_referencia, '%Y-%m')
     - "este ano"        -> WHERE v.ano = YEAR(r.data_referencia)
     - "ultimos N meses" -> WHERE v.data_pedido > DATE_SUB(r.data_referencia, INTERVAL N MONTH)
   A idade do cliente e excecao: ja vem pronta em vw_clientes.idade (calculada com CURDATE()).
8. Os valores de texto do banco estao em ingles. Mapeamento de categorias
   (use o valor da direita no SQL). Isso tem PRIORIDADE sobre a regra 10 (LIKE):
   se a pergunta mencionar um destes termos, filtre por categoria_nome, nunca
   por produto_nome LIKE:
     - livros, livro                                  -> 'Digital Books'
     - celulares, smartphones, telefones               -> 'Cell Phones'
     - tablets                                          -> 'Tablets'
     - notebooks, laptops, computadores portateis       -> 'Notebooks'  (nunca "cadernos")
     - material de escritorio, papelaria                -> 'Office Supply'
9. Estados sao siglas de duas letras dos EUA (CA, NY, TX...). Converta nomes por
   extenso para a sigla (ex.: California -> CA).
10. Busca por nome de produto ou cliente usa LIKE '%termo%'.
11. Toda consulta que lista varias linhas termina com LIMIT (padrao 100 se o
    usuario nao pedir um numero especifico). Agregacoes de uma linha so (sem
    GROUP BY) nao precisam de LIMIT.
12. Aliases de coluna em portugues, sem acento, em snake_case.
13. Se a pergunta nao puder ser respondida com esses dados, ou pedir qualquer
    alteracao/insercao/remocao de dados, retorne pode_responder=false com o motivo
    em vez de tentar gerar um SQL.
"""

FORMATO_SAIDA = """\
Responda APENAS com um JSON no formato abaixo (sem texto antes ou depois, sem bloco markdown):
{"pode_responder": true, "sql": "SELECT ...", "explicacao": "uma frase sobre o que a consulta faz", "motivo": ""}

Quando pode_responder for false, deixe "sql" e "explicacao" como string vazia e
preencha "motivo" com uma frase explicando por que a pergunta nao pode ser respondida.
"""

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "pode_responder": {"type": "boolean"},
        "sql": {"type": "string"},
        "explicacao": {"type": "string"},
        "motivo": {"type": "string"},
    },
    "required": ["pode_responder", "sql", "explicacao", "motivo"],
}


def build_schema_context() -> str:
    return VIEWS_DDL + "\n" + REGRAS + "\n" + FORMATO_SAIDA

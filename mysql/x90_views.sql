1-- Views semanticas para o text2sql.
-- Nome com prefixo "x9" para garantir que rode DEPOIS de dump.sql
-- quando a pasta mysql/ for montada em /docker-entrypoint-initdb.d
-- (ordenacao alfabetica: 'x' > 'd', entao x90_... > dump.sql).
-- So roda automaticamente na PRIMEIRA inicializacao de um volume vazio;
-- em um container ja existente, aplique manualmente via docker exec.

USE mydb;

-- Uma linha por item de pedido (grao mais fino). Parte de tborderdetail
-- com LEFT JOIN porque as FKs sao ON DELETE SET NULL: uma linha orfa
-- (cliente/produto/pedido apagado) nao pode sumir do faturamento.
CREATE OR REPLACE VIEW vw_vendas AS
SELECT
    o.code                                                          AS pedido_id,
    o.orderdate                                                     AS data_pedido,
    YEAR(o.orderdate)                                               AS ano,
    MONTH(o.orderdate)                                              AS mes,
    DATE_FORMAT(o.orderdate, '%Y-%m')                               AS ano_mes,
    c.code                                                          AS cliente_id,
    c.Name                                                          AS cliente_nome,
    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.Address, ',', -2), ',', 1)) AS cliente_cidade,
    TRIM(SUBSTRING_INDEX(c.Address, ',', -1))                       AS cliente_uf,
    p.code                                                          AS produto_id,
    p.description                                                  AS produto_nome,
    p.salevalue                                                     AS preco_catalogo,
    cat.code                                                        AS categoria_id,
    cat.description                                                 AS categoria_nome,
    d.quantity                                                      AS quantidade,
    d.salesvalue                                                    AS valor_total_item,
    ROUND(d.salesvalue / NULLIF(d.quantity, 0), 2)                  AS preco_unitario_praticado
FROM tborderdetail d
LEFT JOIN tborders     o   ON o.code   = d.orders
LEFT JOIN tbcustomers  c   ON c.code   = o.customer
LEFT JOIN tbproducts   p   ON p.code   = d.product
LEFT JOIN tbcategories cat ON cat.code = p.category;

-- Uma linha por cliente.
CREATE OR REPLACE VIEW vw_clientes AS
SELECT
    code                                                            AS cliente_id,
    Name                                                            AS cliente_nome,
    Email                                                           AS email,
    Phone                                                           AS telefone,
    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(Address, ',', -2), ',', 1)) AS cidade,
    TRIM(SUBSTRING_INDEX(Address, ',', -1))                         AS uf,
    BirthDate                                                       AS data_nascimento,
    TIMESTAMPDIFF(YEAR, BirthDate, CURDATE())                       AS idade
FROM tbcustomers;

-- Uma linha por produto.
CREATE OR REPLACE VIEW vw_produtos AS
SELECT
    p.code        AS produto_id,
    p.description AS produto_nome,
    p.salevalue   AS preco_catalogo,
    p.active      AS ativo,
    cat.code      AS categoria_id,
    cat.description AS categoria_nome
FROM tbproducts p
LEFT JOIN tbcategories cat ON cat.code = p.category;

-- Uma linha unica: data de referencia para perguntas com periodo relativo
-- ("ultimo mes", "este ano", "ultimos 12 meses"). Os pedidos nao chegam
-- ate a data de hoje, entao NUNCA usar CURDATE()/NOW() para isso.
CREATE OR REPLACE VIEW vw_referencia AS
SELECT MAX(orderdate) AS data_referencia
FROM tborders;

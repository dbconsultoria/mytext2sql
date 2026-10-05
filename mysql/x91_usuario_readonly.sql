-- Usuario somente leitura usado pela aplicacao text2sql.
-- So enxerga as 4 views semanticas, nunca as tabelas tb* cruas.
-- Nome com prefixo "x9" para garantir que rode DEPOIS de dump.sql e
-- DEPOIS de x90_views.sql (ordenacao alfabetica: x90 < x91).
-- So roda automaticamente na PRIMEIRA inicializacao de um volume vazio;
-- em um container ja existente, aplique manualmente via docker exec.

USE mydb;

CREATE USER IF NOT EXISTS 'texto_sql_ro'@'%' IDENTIFIED BY 'LeituraSegura_2026!';

-- Garante que nao sobrou nenhum privilegio de uma criacao anterior.
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'texto_sql_ro'@'%';

GRANT SELECT ON mydb.vw_vendas     TO 'texto_sql_ro'@'%';
GRANT SELECT ON mydb.vw_clientes   TO 'texto_sql_ro'@'%';
GRANT SELECT ON mydb.vw_produtos   TO 'texto_sql_ro'@'%';
GRANT SELECT ON mydb.vw_referencia TO 'texto_sql_ro'@'%';

FLUSH PRIVILEGES;

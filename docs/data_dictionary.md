# Dicionário de dados: banco `mydb`

Banco de vendas fictício de uma loja de tecnologia e papelaria. Motor: MariaDB (compatível com MySQL). Charset: latin1. Todos os dados (nomes, produtos, categorias, endereços) estão em inglês.

Convenção geral: em todas as tabelas, a coluna `code` é a chave primária (PK) da própria tabela, inteira e auto incremento. As colunas que apontam para outras tabelas usam o nome da entidade referenciada (`customer`, `category`, `product`, `orders`) e sempre referenciam o `code` da tabela de destino.

---

## Visão geral

| Tabela | Papel | Linhas (aprox.) | Granularidade |
|---|---|---|---|
| `tbcategories` | Dimensão | 5 | Uma linha por categoria de produto |
| `tbproducts` | Dimensão | 50 | Uma linha por produto |
| `tbcustomers` | Dimensão | 70 | Uma linha por cliente |
| `tborders` | Fato (cabeçalho) | 3.360 | Uma linha por pedido |
| `tborderdetail` | Fato (itens) | 6.720 | Uma linha por item de pedido (produto dentro de um pedido) |

---

## Relacionamentos declarados no script

Todas as chaves estrangeiras abaixo estão declaradas com `ON DELETE SET NULL`: se o registro pai for apagado, a coluna FK do filho vira `NULL` em vez de o filho ser apagado. Por isso todas as colunas FK aceitam `NULL`, e consultas que precisam incluir linhas órfãs devem usar `LEFT JOIN`.

| Constraint | Tabela filha.coluna | Tabela pai.coluna | Cardinalidade | Significado |
|---|---|---|---|---|
| `fkprodcat` | `tbproducts.category` | `tbcategories.code` | N:1 | Cada produto pertence a no máximo uma categoria; uma categoria tem vários produtos |
| `fkordercustomers` | `tborders.customer` | `tbcustomers.code` | N:1 | Cada pedido pertence a no máximo um cliente; um cliente tem vários pedidos |
| `fkorders` | `tborderdetail.orders` | `tborders.code` | N:1 | Cada item pertence a um pedido; um pedido tem vários itens |
| `fkproddetail` | `tborderdetail.product` | `tbproducts.code` | N:1 | Cada item se refere a um produto; um produto aparece em vários itens |

Consequência: `tborderdetail` funciona como tabela associativa que resolve o relacionamento N:N entre `tborders` e `tbproducts`.

Caminho de join completo:

```
tbcategories.code  <-  tbproducts.category
tbproducts.code    <-  tborderdetail.product
tborders.code      <-  tborderdetail.orders
tbcustomers.code   <-  tborders.customer
```

```sql
FROM tborderdetail d
LEFT JOIN tborders     o   ON o.code   = d.orders
LEFT JOIN tbcustomers  c   ON c.code   = o.customer
LEFT JOIN tbproducts   p   ON p.code   = d.product
LEFT JOIN tbcategories cat ON cat.code = p.category
```

Diagrama:

```
tbcategories 1 ──< N tbproducts 1 ──< N tborderdetail N >── 1 tborders N >── 1 tbcustomers
```

---

## `tbcategories`

Categorias de produto.

| Coluna | Tipo | Nulo | Chave | Descrição |
|---|---|---|---|---|
| `code` | int | Não | PK | Identificador da categoria |
| `description` | varchar(150) | Sim | | Nome da categoria, em inglês |

Valores existentes e equivalência em português (use o valor em inglês no SQL):

| `code` | `description` | Termos em português que o usuário pode usar |
|---|---|---|
| 1 | `Books` | livros |
| 2 | `Cell Phones` | celulares, smartphones, telefones |
| 3 | `Tablets` | tablets |
| 4 | `Notebooks` | notebooks, laptops, computadores portáteis (NÃO significa cadernos) |
| 5 | `Office Supply` | material de escritório, papelaria, móveis de escritório |

---

## `tbproducts`

Catálogo de produtos. São 10 produtos por categoria.

| Coluna | Tipo | Nulo | Chave | Descrição |
|---|---|---|---|---|
| `code` | int | Não | PK | Identificador do produto |
| `description` | varchar(150) | Sim | | Nome do produto, em inglês (ex.: `MacBook Air M2`, `Clean Code Book`) |
| `salevalue` | decimal(18,2) | Sim | | Preço de catálogo (tabela) do produto, por unidade |
| `active` | int | Sim | | Indicador de produto ativo: 1 = ativo, 0 = inativo. Hoje todos são 1 |
| `category` | int | Sim | FK → `tbcategories.code` | Categoria do produto |

Atenção: `salevalue` (catálogo) é diferente de `tborderdetail.salesvalue` (valor efetivamente vendido). Os nomes são parecidos, mas não são a mesma coisa.

---

## `tbcustomers`

Cadastro de clientes, todos nos Estados Unidos.

| Coluna | Tipo | Nulo | Chave | Descrição |
|---|---|---|---|---|
| `code` | int | Não | PK | Identificador do cliente |
| `Name` | varchar(100) | Sim | | Nome completo (com N maiúsculo no nome da coluna) |
| `Address` | varchar(250) | Sim | | Endereço completo em campo único |
| `Phone` | varchar(25) | Sim | | Telefone no formato `DDD-NNNNNNN` (ex.: `212-5550001`) |
| `Email` | varchar(100) | Sim | | E-mail |
| `BirthDate` | datetime | Sim | | Data de nascimento (hora sempre 00:00:00) |

Formato de `Address`: `<número> <rua>, <cidade>, <UF>` com UF de duas letras. Exemplo: `101 Main Street, New York, NY`.

Extração de cidade e UF:

```sql
TRIM(SUBSTRING_INDEX(c.Address, ',', -1))                            AS uf
TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.Address, ',', -2), ',', 1))   AS cidade
```

UFs presentes: NY, IL, TX, FL, WA, CO, MA, AZ, OR, WI, CA (maioria absoluta em CA).

Os valores de `code` dependem de como a carga foi feita (no dump vão de 71 a 140; numa carga limpa do script vão de 1 a 70). Nunca presuma valores fixos de `code` de cliente.

---

## `tborders`

Cabeçalho do pedido.

| Coluna | Tipo | Nulo | Chave | Descrição |
|---|---|---|---|---|
| `code` | int | Não | PK | Número do pedido |
| `customer` | int | Sim | FK → `tbcustomers.code` | Cliente que fez o pedido |
| `orderdate` | timestamp | Não | | Data e hora do pedido (padrão `CURRENT_TIMESTAMP`) |

O pedido não tem valor total gravado. O total do pedido é a soma de `tborderdetail.salesvalue` dos seus itens.

---

## `tborderdetail`

Itens do pedido. Esta tabela não tem chave primária declarada.

| Coluna | Tipo | Nulo | Chave | Descrição |
|---|---|---|---|---|
| `product` | int | Sim | FK → `tbproducts.code` | Produto vendido |
| `orders` | int | Sim | FK → `tborders.code` | Pedido ao qual o item pertence. Atenção: o nome da coluna é `orders`, no plural, mas guarda o `code` de UM pedido |
| `quantity` | int | Sim | | Quantidade vendida do produto no item (1 a 5) |
| `salesvalue` | decimal(18,2) | Sim | | Valor TOTAL do item (já multiplicado pela quantidade) |

Regras importantes:

- `salesvalue` já é o total da linha. Faturamento = `SUM(salesvalue)`. Nunca multiplique `salesvalue` por `quantity`.
- O preço unitário praticado é `salesvalue / quantity`.
- O preço praticado NÃO bate com `tbproducts.salevalue`. Para qualquer pergunta sobre vendas, faturamento ou receita, use `salesvalue`. Use `tbproducts.salevalue` apenas para perguntas sobre preço de catálogo ou tabela.

---

## Glossário de métricas de negócio

| Termo do usuário | Definição em SQL |
|---|---|
| Faturamento, receita, vendas em valor, total vendido | `SUM(d.salesvalue)` |
| Quantidade vendida, unidades vendidas | `SUM(d.quantity)` |
| Número de pedidos | `COUNT(DISTINCT o.code)` |
| Número de itens / linhas vendidas | `COUNT(*)` em `tborderdetail` |
| Ticket médio | `SUM(d.salesvalue) / COUNT(DISTINCT o.code)` |
| Preço médio praticado | `SUM(d.salesvalue) / SUM(d.quantity)` |
| Preço de catálogo | `p.salevalue` |
| Clientes ativos (que compraram) | `COUNT(DISTINCT o.customer)` |
| Idade do cliente | `TIMESTAMPDIFF(YEAR, c.BirthDate, CURDATE())` |

---

## Período dos dados e datas relativas

- Os pedidos vão de 2022-01-15 até 2025-12-15.
- Todo cliente faz exatamente um pedido por mês, sempre no dia 15 às 10:00.
- Os dados NÃO chegam até a data de hoje. Para perguntas com período relativo ("último mês", "este ano", "últimos 12 meses"), use como data de referência `(SELECT MAX(orderdate) FROM tborders)` e não `CURDATE()` ou `NOW()`.
- Exceção: idade de cliente é calculada em relação a `CURDATE()`.

---

## Características dos dados (sintéticos)

Os dados foram gerados por script, o que explica alguns padrões:

- 70 clientes × 48 meses = 3.360 pedidos, então todos os clientes têm o mesmo número de pedidos.
- Cada pedido tem de 1 a 3 itens, sempre com produtos diferentes.
- `salesvalue` vai de 50 a 1.245.
- Rankings de clientes por número de pedidos sempre empatam. Rankings por faturamento não empatam.

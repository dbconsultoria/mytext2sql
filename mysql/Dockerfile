FROM mysql:8.0

# Copiar o dump para ser executado na inicialização
COPY dump.sql /docker-entrypoint-initdb.d/

# Variáveis de ambiente padrão (podem ser sobrescritas)
ENV MYSQL_ROOT_PASSWORD=mypswd
ENV MYSQL_DATABASE=mydb
ENV MYSQL_USER=myusr
ENV MYSQL_PASSWORD=mypswd

# Expor a porta padrão do MySQL
EXPOSE 3306
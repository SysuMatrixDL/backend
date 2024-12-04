import os

DB_HOST = os.getenv("DB_HOST", "open-gauss")  # docker-compose hostname
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "superuser")
DB_PWD = os.getenv("DB_PWD", "OGSql@123")
DB_CONNECT_DB = os.getenv("DB_CONNECT_DB", "postgres")
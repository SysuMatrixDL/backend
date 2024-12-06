import os
import socket

# PRODUCTION 表示开发环境, DEVELOPMENT 表示生产环境
MATRIXDL_ENVIROMENT = os.getenv("MATRIXDL_ENVIROMENT", "DEVELOPMENT")
MATRIXDL_WORKER = os.getenv("MATRIXDL_WORKERT", "1")

BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")

DB_HOST = os.getenv("DB_HOST", "open-gauss")  # docker-compose hostname
try:
  DB_IP = socket.gethostbyname(DB_HOST)
except socket.gaierror as e:
  DB_IP = "172.18.198.206"
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "superuser")
DB_PWD = os.getenv("DB_PWD", "OGSql@123")
DB_CONNECT_DB = os.getenv("DB_CONNECT_DB", "postgres")
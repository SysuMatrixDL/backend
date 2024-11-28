# pip install psycopg2-binary
# python连接OpenGauss数据库
from psycopg2 import connect

class OpenGaussConnector:
    def __init__(self, ip, port, user, pwd, database) -> None:
        params = {
            'database': database,
            'user': user,
            'password': pwd,
            'host': ip,
            'port': port
        }
        self.conn = connect(**params)
    
    def exec(self, cmd:str):
        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(cmd)
                result = cursor.fetchone()
        return result

if __name__ == "__main__":
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='superuser', pwd='OGSql@123', database='postgres')
    cmd = 'select * from PG_ROLES;'
    res = db.exec(cmd)
    print(res)
# pip install psycopg2-binary
# python连接OpenGauss数据库
from psycopg2 import connect
import psycopg2

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
                try:
                    result = cursor.fetchall()
                except psycopg2.ProgrammingError as e:
                    if str(e).strip() == 'no results to fetch':
                        return None
                    else:
                        raise e
        return result
    
    def get_one_res(self, cmd:str):
        res = self.exec(cmd)
        if len(res) == 0:
            return None
        elif len(res) > 1:
            raise Exception(f"more than 1 result, cmd={cmd}")
        else:
            return res[0]

if __name__ == "__main__":
    db = OpenGaussConnector(
        ip=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        pwd=DB_PWD,
        database=DB_CONNECT_DB
    )
    # cmd = 'SELECT * FROM pg_tables where tableowner = \'superuser\';'
    cmd = 'insert into gpu values (2, \'asas\')'
    res = db.exec(cmd)
    print(res)
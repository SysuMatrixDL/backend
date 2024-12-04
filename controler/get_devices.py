from common.connect import OpenGaussConnector
from config import *

def get_devices(db:OpenGaussConnector):
    """
    获取当前所有设备的did, 返回一个列表
    例如[1, 2, 3]
    """
    cmd = f'select did from device'
    res = db.exec(cmd)
    res = [r[0] for r in res]
    return res

if __name__ == "__main__":
    db = OpenGaussConnector(
        host=DB_IP,
        port=DB_PORT,
        user=DB_USER,
        pwd=DB_PWD,
        database=DB_CONNECT_DB
    )
    print(get_devices(db))
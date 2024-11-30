from connect import OpenGaussConnector

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
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='superuser', pwd='OGSql@123', database='postgres')
    print(get_devices(db))
from connect import OpenGaussConnector

def get_devices(db:OpenGaussConnector):
    cmd = f'select did from devices'
    res = db.exec(cmd)
    res = [r[0] for r in res]
    return res
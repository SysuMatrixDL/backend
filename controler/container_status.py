from common.connect import OpenGaussConnector
import docker
from config import *

def container_status(db:OpenGaussConnector, cid:int, uid:int=None):
    # 验证用户身份
    if uid is not None:
        cmd = f'select cid from containers where uid = {uid} and cid = {cid}'
        res = db.exec(cmd)
        if len(res) == 0:
            return -1, f'no container or not authorized to visit'
    # 获取旧容器状态
    cmd = f'select status from containers where cid = {cid}'
    old_status = db.get_one_res(cmd)[0]
    # 获取设备ip
    cmd = f'select ip from device where did = (select did from images where iid = ( select iid from containers where cid = {cid}))'
    ip = db.get_one_res(cmd)[0]
    # 更新容器状态
    client = docker.APIClient(base_url=f'ssh://root@{ip}')
    containers = client.containers(all=True)
    new_status = None
    for c in containers:
        if c['Names'] == [f'/c{cid}']:
            if c['State'] == 'running':
                new_status = 'running'
            else:
                new_status = 'stopped'
            break
    if new_status is None:
        # 删除容器
        cmd = f'delete from containers where cid = {cid}'
        db.exec(cmd)
        return -1, f'no container or not authorized to visit'
    if new_status != old_status:
        # print('set new status')
        cmd = f'update containers set status = \'{new_status}\' where cid = {cid}'
        db.exec(cmd)
    
    return 0, new_status

if __name__ == "__main__":
    db = OpenGaussConnector(
        host=DB_IP,
        port=DB_PORT,
        user=DB_USER,
        pwd=DB_PWD,
        database=DB_CONNECT_DB
    )
    print(container_status(db, 1, 1))
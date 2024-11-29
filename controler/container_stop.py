from connect import OpenGaussConnector
from container_status import container_status
import subprocess

def container_stop(db:OpenGaussConnector, cid:int, uid:int=None):
    # 验证用户身份
    if uid is not None:
        cmd = f'select cid from containers where uid = {uid} and cid = {cid}'
        res = db.exec(cmd)
        if len(res) == 0:
            return -1, f'no container or not authorized to visit'
    # 更新容器状态
    ret, status = container_status(db, cid)
    if ret!=0:
        return ret, status
    if status == 'exited':
        return -1, 'container already stopped'
    

    # 获取容器gpu
    cmd = f'select gid from container_gpu where cid = {cid}'
    res = db.exec(cmd)
    gid = None if len(res) == 0 else res[0][0]
    
    # 获取设备ip
    cmd = f'select ip from device where did = (select did from images where iid = ( select iid from containers where cid = {cid}))'
    ip = db.get_one_res(cmd)[0]

    # 停止容器
    docker_cmd = f'docker -H ssh://root@{ip} stop c{cid}'
    out = subprocess.run(docker_cmd, capture_output=True, shell=True)
    # 更新container表
    cmd = f'update containers set status = \'exited\' where cid = {cid}'
    db.exec(cmd)
    
    # 更新container_gpu表
    if gid is not None:
        cmd = f'delete from container_gpu where cid = {cid}'
        db.exec(cmd)
    
    return 0, 'success'

if __name__ == "__main__":
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='superuser', pwd='OGSql@123', database='postgres')
    print(container_stop(db, 1, 1))
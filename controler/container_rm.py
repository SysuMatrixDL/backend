from connect import OpenGaussConnector
from container_status import container_status
from container_stop import container_stop
import subprocess

def container_rm(db:OpenGaussConnector, cid:int, uid:int):
    # 验证用户身份
    cmd = f'select cid from containers where uid = {uid} and cid = {cid}'
    res = db.exec(cmd)
    if len(res) == 0:
        return -1, f'no container or not authorized to visit'
    
    # 更新容器状态
    ret, status = container_status(db, cid)
    if ret!=0:
        return ret, status
    if status == 'running':
        ret, status = container_stop(db, cid)
        if ret != 0:
            return ret, status
    # 获取设备ip
    cmd = f'select ip from device where did = (select did from images where iid = ( select iid from containers where cid = {cid}))'
    ip = db.get_one_res(cmd)[0]

    # 删除容器
    docker_cmd = f'docker -H ssh://root@{ip} rm c{cid}'
    out = subprocess.run(docker_cmd, capture_output=True, shell=True)
    if out.returncode != 0:
        return -1, f'docker failed with message {out.stderr.decode('utf-8')}'
    # 更新container表
    cmd = f'delete from containers where cid = {cid}'
    db.exec(cmd)
    
    return 0, 'success'
    
if __name__ == "__main__":
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='superuser', pwd='OGSql@123', database='postgres')
    print(container_rm(db, 1, 1))
from controler.connect import OpenGaussConnector
from controler.container_status import container_status
import subprocess

def container_start(db:OpenGaussConnector, cid:int, uid:int, gid:int):
    # 验证用户身份
    cmd = f'select cid from containers where uid = {uid} and cid = {cid}'
    res = db.exec(cmd)
    if len(res) == 0:
        return -1, f'no container or not authorized to visit'
    
    ret, status = container_status(db, cid)
    if ret!=0:
        return ret, status
    if status == 'running':
        return -1, 'container already running'
    
    # 获取容器cpu,mem
    cmd = f'select cpu, memory from containers where cid = {cid}'
    cpu, mem = db.get_one_res(cmd)
    
    # 获取总cpu, memory
    cmd = f'select did, real_id from images where iid = (select iid from containers where cid = {cid});'
    did, real_id = db.get_one_res(cmd)
    cmd = f'select ip, cpu, memory, data_dir, pub_dir from device where did = {did};'
    ip, total_cpu, total_memory, _ ,_ = db.get_one_res(cmd)
    # 计算已经使用的cpu和内存资源
    cmd = f'select sum(c.cpu), sum(c.memory) from containers c left join images i on c.iid = i.iid where i.did = {did} and c.status = \'running\''
    used_cpu, used_memory = db.get_one_res(cmd)
    if used_cpu is None:
        used_cpu = 0
    if used_memory is None:
        used_memory = 0
    if used_cpu + cpu > total_cpu or used_memory + mem > total_memory:
        return -1, 'cpu or memory not enough'
    # 判断gpu是否可用
    if gid is not None:
        cmd = f'select gid from container_gpu where gid = {gid} and cid != {cid}'
        if len(db.exec(cmd)) > 0:
            return -1, f'gpu {gid} not available'

    # 启动！
    docker_cmd = f'docker -H ssh://root@{ip} start c{cid}'
    out = subprocess.run(docker_cmd, capture_output=True, shell=True)
    if out.returncode != 0:
        return -1, f'docker failed with message {out.stderr.decode('utf-8')}'
    # 更新container表
    cmd = f'update containers set status = \'running\' where cid = {cid}'
    db.exec(cmd)
    
    # 更新container_gpu表
    if gid is not None:
        cmd = f'insert into container_gpu (cid, gid) values ({cid}, {gid})'
        db.exec(cmd)
    
    return 0, 'success'

if __name__ == "__main__":
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='superuser', pwd='OGSql@123', database='postgres')
    print(container_start(db, 1, 1, 1))
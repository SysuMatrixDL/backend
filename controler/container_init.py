from common.connect import OpenGaussConnector
import subprocess
import secrets, os
import string
from config import *

def generate_random_password(length=16):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def get_port(db:OpenGaussConnector, ip:int):
    
    ret = subprocess.run(f'ssh root@{ip} "python ~/.matrixdl/bind_port.py"', capture_output=True, shell=True)
    out = ret.stdout.decode('utf-8')
    out = out.strip().split(' ')
    out = [int(i) for i in out]
    return out

def get_id(db:OpenGaussConnector, id, table):
    cmd = f'select max({id})+1 from {table};'
    res = db.get_one_res(cmd)[0]
    if res is None:
        return 1
    else:
        return res

def container_init(db:OpenGaussConnector, iid:int, uid:int, name:str, cpu:int, mem:int, gid:int | None):
    # 核验身份
    cmd = f'select iid, did from images'
    res = db.exec(cmd)
    if len(res) == 0:
        return -1, 'no image or not authorized to visit image'
    # 获取设备编号
    cmd = f'select did, real_id from images where iid = {iid};'
    did, real_id = db.get_one_res(cmd)
    cmd = f'select ip, cpu, memory, data_dir, pub_dir from device where did = {did};'
    ip, total_cpu, total_memory, data_dir, pub_dir = db.get_one_res(cmd)
    cid = get_id(db, 'cid', 'containers')
    container_data_dir = os.path.join(data_dir, str(cid))

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
        cmd = f'select gid from container_gpu where gid = {gid}'
        if len(db.exec(cmd)) > 0:
            return -1, f'gpu {gid} not available'
    # 获取端口
    portssh, portjupyter, porttsb = get_port(db, ip)
    # 随机密码
    passwd = generate_random_password()
    
    # 启动容器
    docker_cmd = f'docker -H ssh://root@{ip} run '
    if gid is not None:
        docker_cmd += f'--gpus all '
    docker_cmd += f'-d -it -e JUPYTER_TOKEN={passwd} -v {container_data_dir}:/workspace -v {pub_dir}:/pub_data -p {portssh}:22 -p {portjupyter}:8888 -p {porttsb}:6006 --name c{cid} --cpus={cpu} -m {mem}m -d {real_id}'
    
    # print(docker_cmd)
    
    out = subprocess.run(docker_cmd, capture_output=True, shell=True)
    # print(out)
    if out.returncode != 0:
        return -1, f"docker failed with message {out.stderr.decode('utf-8')}"
    # 更新container表
    cmd = f'insert into containers (cid, uid, iid, name, cpu, memory, portssh, portjupyter, porttsb, passwd, status) values ({cid}, {uid}, {iid}, \'{name}\', {cpu}, {mem}, {portssh}, {portjupyter}, {porttsb}, \'{passwd}\', \'running\')'
    db.exec(cmd)
    # 更新container_gpu表
    if gid is not None:
        cmd = f'insert into container_gpu (cid, gid) values ({cid}, {gid})'
        db.exec(cmd)
    
    return 0, f"passwd:\'{passwd}\', portssh:{portssh}, portjupyter:{portjupyter}, porttsb:{porttsb}"
    
    
    

if __name__ == "__main__":
    db = OpenGaussConnector(
        ip=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        pwd=DB_PWD,
        database=DB_CONNECT_DB
    )
    print(container_init(db, 1, 1, 'test', 2, 2048, 1))
    
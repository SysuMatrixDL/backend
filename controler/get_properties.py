import docker

from config import *

from common.connect import OpenGaussConnector


def get_containers(db:OpenGaussConnector, uid:int):
    """
    以列表形式返回用户uid的所有容器的cid
    例如[1,2,3]
    """
    cmd = f'select cid from containers where uid = {uid}'
    res = db.exec(cmd)
    res = [r[0] for r in res]
    return res

def get_user_images(db:OpenGaussConnector, uid:int):
    """
    以列表形式返回用户uid创建的所有镜像的iid
    例如[1,2,3]
    """
    cmd = f'select iid from images where iid in (select iid from user_images where uid = {uid})'
    res = db.exec(cmd)
    res = [r[0] for r in res]
    return res

def get_public_images(db:OpenGaussConnector):
    """
    以列表形式返回所有公共镜像的iid
    例如[1,2,3]
    """
    cmd = f'select iid from images where public = TRUE'
    res = db.exec(cmd)
    res = [r[0] for r in res]
    return res

def get_device_images(db:OpenGaussConnector, did:int, name: str):
    """
    以列表形式返回设备 did 上的所有镜像的 iid 和所属的用户名，如果镜像是公有的，则用户名返回public，私有且不是uid用户的则不返回
    示例：
    [{'iid': 1, 'User': 'public', 'public':'true'}, {'iid': 2, 'User': 'admin', 'public':'false'}]
    """
    cmd = f'select i.iid, i.name, u.name, i.public from images i left join user_images ui on i.iid = ui.iid left join "User" u on ui.uid = u.uid where i.did={did}'
    res = db.exec(cmd)
    res = [{'iid':r[0], 'name': r[1], 'User': 'public'if r[2] is None else r[2], 'public': r[3] } for r in res if r[2] is None or r[2] == name]
    return res

def device_property(db:OpenGaussConnector, did:int):
    """
    获取设备的所有硬件和使用情况属性
    示例：
    ```python
    names = ['total_cpu', 'used_cpu', 'cpu_name', 'total_memory', 'used_memory', 'gpus', 'gpu_used', 'ip']
    res = device_property(db, 1)
    for i in range(len(res)):
        print(names[i], ': ', res[i])
    ```
    输出结果：
    ```
    total_cpu :  26
    used_cpu :  0
    cpu_name :  Intel(R) Core(TM) i7-14700K
    total_memory :  24576
    used_memory :  0
    gpus :  [(1, 'RTX4060 Ti 16GB')]
    gpu_used :  []
    ip : 114.114.114.114
    ```
    """
    # 获取设备所有资源
    cmd = f'select ip, cpu, memory, data_dir, pub_dir, cpu_name from device where did = {did};'
    ip, total_cpu, total_memory, data_dir, pub_dir, cpu_name = db.get_one_res(cmd)
    # 获取设备已经使用的cpu和mem资源
    cmd = f'select sum(c.cpu), sum(c.memory) from containers c left join images i on c.iid = i.iid where i.did = {did} and c.status = \'running\''
    used_cpu, used_memory = db.get_one_res(cmd)
    if used_cpu is None:
        used_cpu = 0
    if used_memory is None:
        used_memory = 0
    # 获取设备所有gpu
    cmd = f'select g.gid ,g.type from gpu_device d join gpu g on g.gid = d.gid where d.did = {did}'
    gpus = db.exec(cmd)
    # 获取已使用的gpu
    cmd = f'select c.gid from container_gpu c join gpu_device g on c.gid = g.gid where g.did = {did} and c.used = 1'
    gpu_used = db.exec(cmd)
    
    return total_cpu, used_cpu, cpu_name, total_memory, used_memory, gpus, gpu_used, ip


def container_property_query(cid):
    return f"\
    SELECT\
        co.name, co.cpu, co.memory, co.portssh, co.portjupyter, co.porttsb, co.passwd, d.ip, d.cpu_name, gpu.type\
    FROM\
        containers co\
        LEFT JOIN images i ON co.iid = i.iid\
        LEFT JOIN device d ON d.did = i.did\
        LEFT JOIN container_gpu cg ON cg.cid = {cid}\
        LEFT JOIN gpu ON cg.gid = gpu.gid\
    WHERE\
        co.CID = {cid};\
".strip()

def container_property(db:OpenGaussConnector, cid:int):
    """
    获取容器的所有资源属性
    """
    cmd = container_property_query(cid)
    name, cpu, memory, portssh, portjupyter, porttsb, passwd, ip, cpu_name, gpu_type = db.get_one_res(cmd)
    return name, cpu, memory, portssh, portjupyter, porttsb, passwd, ip, cpu_name, '无GPU' if gpu_type is None else gpu_type


def image_property(db:OpenGaussConnector, iid:int):
    cmd = f'select i.real_id, i.iid, i.did, i.name, i.public, u.name, i.size from images i left join user_images ui on i.iid = ui.iid left join "User" u on ui.uid = u.uid where i.iid = {iid}'
    real_id, _, did, name, public, user, size = db.get_one_res(cmd)
    res = {'did': did, 'name': name, 'public': public, 'user':'public' if user is None else user, 'size': size}
    return res
    

if __name__ == '__main__':
    db = OpenGaussConnector(
        host=DB_IP,
        port=DB_PORT,
        user=DB_USER,
        pwd=DB_PWD,
        database=DB_CONNECT_DB
    )
    print(get_containers(db, 1))
    print(get_device_images(db, 1))
    print(get_user_images(db, 1))
    names = ['total_cpu', 'used_cpu', 'cpu_name', 'total_memory', 'used_memory', 'gpus', 'gpu_used', 'images']
    res = device_property(db, 1)
    for i in range(len(res)):
        print(names[i], ': ', res[i])
    print(image_property(db, 1))
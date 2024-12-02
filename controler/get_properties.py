from connect import OpenGaussConnector

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
    cmd = f'select iid from images where iid not in (select iid from user_images where uid != {uid})'
    res = db.exec(cmd)
    res = [r[0] for r in res]
    return res

def get_device_images(db:OpenGaussConnector, did:int):
    """
    以列表形式返回设备did上的所有镜像的iid和所属的用户名，如果镜像是公有的，则用户名返回public
    示例：
    [{'iid': 1, 'User': 'public'}, {'iid': 2, 'User': 'admin'}]
    """
    cmd = f'select i.iid, u.name from images i left join user_images ui on i.iid = ui.uid left join "User" u on ui.uid = u.uid where i.did={did}'
    res = db.exec(cmd)
    res = [{'iid':r[0], 'User': 'public' if r[1] is None else r[1]} for r in res]
    return res

def device_property(db:OpenGaussConnector, did:int):
    """
    获取设备的所有资源属性
    示例：
    ```python
    names = ['total_cpu', 'used_cpu', 'cpu_name', 'total_memory', 'used_memory', 'gpus', 'gpu_used', 'images']
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
    images :  [(1,)]
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
    cmd = f'select c.gid from container_gpu c join gpu_device g on c.gid = g.gid where g.did = {did}'
    gpu_used = db.exec(cmd)
    # # 获取所有镜像
    # cmd = f'select iid from images where did = {did}'
    # images = db.exec(cmd)
    images = get_device_images(db, did)
    
    return total_cpu, used_cpu, cpu_name, total_memory, used_memory, gpus, gpu_used, images
    
def image_property(db:OpenGaussConnector, iid:int):
    cmd = f'select i.iid, i.did, i.name, u.name from images i left join user_images ui on i.iid = ui.iid left join "User" u on ui.uid = u.uid where i.iid = {iid}'
    r = db.get_one_res(cmd)
    res = {'iid':r[0], 'did':r[1], 'name':r[2], 'user':'public' if r[3] is None else r[3]}
    return res
    

if __name__ == '__main__':
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='superuser', pwd='OGSql@123', database='postgres')
    print(get_containers(db, 1))
    print(get_device_images(db, 1))
    print(get_user_images(db, 1))
    names = ['total_cpu', 'used_cpu', 'cpu_name', 'total_memory', 'used_memory', 'gpus', 'gpu_used', 'images']
    res = device_property(db, 1)
    for i in range(len(res)):
        print(names[i], ': ', res[i])
    print(image_property(db, 1))
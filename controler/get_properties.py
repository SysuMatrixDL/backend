from connect import OpenGaussConnector

def get_containers(db:OpenGaussConnector, uid:int):
    cmd = f'select cid from containers where uid = {uid}'
    res = db.exec(cmd)
    res = [r[0] for r in res]
    return res

def get_images(db:OpenGaussConnector, uid:int):
    cmd = f'select iid from images where iid not in (select iid from user_images where uid != {uid})'
    res = db.exec(cmd)
    res = [r[0] for r in res]
    return res

def device_property(db:OpenGaussConnector, did:int):
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
    # 获取所有镜像
    cmd = f'select iid from images where did = {did}'
    images = db.exec(cmd)
    
    return total_cpu, used_cpu, cpu_name, total_memory, used_memory, gpus, gpu_used, images
    
    
    

if __name__ == '__main__':
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='superuser', pwd='OGSql@123', database='postgres')
    print(get_containers(db, 1))
    print(get_images(db, 1))
    names = ['total_cpu', 'used_cpu', 'cpu_name', 'total_memory', 'used_memory', 'gpus', 'gpu_used', 'images']
    res = device_property(db, 1)
    for i in range(len(res)):
        print(names[i], ': ', res[i])
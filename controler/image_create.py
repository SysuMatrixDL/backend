from connect import OpenGaussConnector
import subprocess

def get_id(db:OpenGaussConnector, id, table):
    cmd = f'select max({id})+1 from {table};'
    res = db.get_one_res(cmd)[0]
    if res is None:
        return 1
    else:
        return res

def image_create(db:OpenGaussConnector, cid:int, name:str, uid:int):
    """
    返回两个值，第一个值为0表示执行成功，第二个值在执行成功时表示新创建的镜像的iid，否则为报错信息
    """
    # 验证用户身份
    
    cmd = f'select cid from containers where uid = {uid} and cid = {cid}'
    res = db.exec(cmd)
    if len(res) == 0:
        return -1, f'no container or not authorized to visit'
    # 获取设备ip
    cmd = f'select did, ip from device where did = (select did from images where iid = ( select iid from containers where cid = {cid}))'
    did, ip = db.get_one_res(cmd)
    
    # 容器->镜像
    docker_cmd = f'docker -H ssh://root@{ip} commit c{cid}'
    out = subprocess.run(docker_cmd, capture_output=True, shell=True)
    out = out.stdout.decode('utf-8').strip()
    real_id = out[len('sha256:'):]

    # 获取iid
    iid = get_id(db, 'iid', 'images')
    # 更新images表
    cmd = f'insert into images values ({iid}, {did}, \'{name}\', \'{real_id}\')'
    db.exec(cmd)
    # 更新user_images表
    cmd = f'insert into user_images values ({uid}, {iid})'
    db.exec(cmd)
    return 0, iid

if __name__ == "__main__":
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='superuser', pwd='OGSql@123', database='postgres')
    print(image_create(db, 1, 'mytest', 1))
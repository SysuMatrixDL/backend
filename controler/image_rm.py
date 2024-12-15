import subprocess

from config import *

from common.connect import OpenGaussConnector


def image_rm(db:OpenGaussConnector, iid:int, uid:int):
    # 验证用户身份
    cmd = f'select * from user_images where iid = {iid} and uid = {uid}'
    res = db.exec(cmd)
    if len(res) == 0:
        return -1, f'no image or not authorized to remove'
    # 验证是否存在容器和镜像关联
    cmd = f'select * from containers where iid = {iid}'
    res = db.exec(cmd)
    if len(res) != 0:
        return -1, f'some containers is based on the image, unable to remove image'
    # 获取设备ip
    cmd = f'select ip from device where did = (select did from images where iid = {iid})'
    ip = db.get_one_res(cmd)[0]
    # 获取镜像真实id
    cmd = f'select real_id from images where iid = {iid}'
    real_id = db.get_one_res(cmd)[0]
    # 删除镜像
    docker_cmd = f'docker -H ssh://root@{ip} rmi {real_id}'
    out = subprocess.run(docker_cmd, capture_output=True, shell=True)
    if out.returncode != 0:
        message = out.stderr.decode('utf-8')
        if not message.find('No such image'):  # 本就不存在的虚空镜像也返回成功删除
            return -1, message
    # 更新数据库
    cmd = f'delete from images where iid = {iid}'
    db.exec(cmd)
    cmd = f'delete from user_images where iid = {iid}'
    db.exec(cmd)
    return 0, 'success'

if __name__ == "__main__":
    db = OpenGaussConnector(
        host=DB_IP,
        port=DB_PORT,
        user=DB_USER,
        pwd=DB_PWD,
        database=DB_CONNECT_DB
    )
    print(image_rm(db, 2, 1))
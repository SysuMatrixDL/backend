from typing import List, Optional
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import *

from common.connect import OpenGaussConnector
import common.user_valid as user_valid

from controler.container_init import container_init
from controler.container_status import container_status
from controler.container_start import container_start
from controler.container_stop import container_stop
from controler.container_rm import container_rm
from controler.get_properties import container_property, get_containers

router = APIRouter()


class CreateRequest(BaseModel):
    iid: int
    name: str
    cpu: int
    mem: int
    gid: List[int]

# 目前只支持一个容器一个gpu,前端支持选多个,这里对多个gpu直接返回错误
@router.post("/create")
def create_container(container_req: CreateRequest, req: Request):
    try:
        if len(container_req.gid) > 1:
            return JSONResponse(
                content={"status": -1, "error": "目前只支持一个容器一个 gpu !"}, status_code=422
            )
        # Create database connection
        db = OpenGaussConnector(
            host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
        )

        status, message = user_valid.user_exists(db, req)
        if status == False:
            return JSONResponse(
                content={"status": -1, "error": message}, status_code=401
            )
        username = req.cookies.get("username")
        cmd = f"select uid from \"User\" where name = '{username}'"
        uid = db.get_one_res(cmd)[0]
        # Call container initialization handler with database connection
        status, message = container_init(
            db=db,
            iid=container_req.iid,
            uid=uid,
            name=container_req.name,
            cpu=container_req.cpu,
            mem=container_req.mem,
            gid= None if len(container_req.gid) is 0 else container_req.gid[0],
        )

        if status == 0:
            # Parse the success message into individual components
            info = dict(item.split(":") for item in message.split(", "))
            return JSONResponse(
                content={
                    "status": 0,
                    "passwd": info["passwd"].strip("'"),
                    "portssh": int(info["portssh"]),
                    "portjupyter": int(info["portjupyter"]),
                    "porttsb": int(info["porttsb"]),
                }
            )
        else:
            return JSONResponse(
                content={"status": -1, "error": message}, status_code=500
            )

    except Exception as e:
        raise e


@router.get("")
def list_containers(req: Request):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)
    
    user_token = req.cookies.get("user_token")
    cmd = f"select uid from \"User\" where user_token = '{user_token}'"
    uid = db.get_one_res(cmd)[0]  # 获取查询结果第一个,预期查询结果就只有一个

    ret = get_containers(db, uid)
    ret = jsonable_encoder(ret)
    return JSONResponse(content={"status": 0, "cid": ret})


class UpdateRequest(BaseModel):
    cmd: str


@router.put("/{cid}")
def update_container(req: Request, update_req: UpdateRequest, cid: int):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    username = req.cookies.get("username")
    cmd = f"SELECT uid from \"User\" where name ='{username}'"
    uid = db.get_one_res(cmd)[0]

    try:
        if update_req.cmd == "start":
            # igonre gid
            status_code,status = container_start(db, cid, uid, None)
            if status_code == -1:
                return JSONResponse(content={"status":-1, "error":status}, status_code=500)
            elif status_code == 0:
                return JSONResponse(content={"status":0})
            else:
                raise Exception("Unkown status_code")
        elif update_req.cmd == "stop":
            status_code,status = container_stop(db,cid,uid)
            if status_code == -1:
                return JSONResponse(content={"status":-1, "error":status}, status_code=500)
            elif status_code == 0:
                return JSONResponse(content={"status":0})
            else:
                raise Exception("Unkown status_code")
        else:
            return JSONResponse(
                content={"status": -1, "error": "unknown command"}, status_code=500
            )
    except Exception as e:
        raise e


class StatusRequest(BaseModel):
    cid: Optional[int] = None
    uid: Optional[int] = None


@router.get("/status/{cid}")
def get_container_status(req: Request, cid: int):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)
    try:
        status_code, status = container_status(db, cid, None)
        if status_code == -1:
            return JSONResponse(
                content={"status": -1, "error": status}, status_code=500
            )
        elif status_code == 0:
            return JSONResponse(content={"status": 0, "result": status})
        else:
            return JSONResponse(
                content={"status": -1, "error": "Unknown error"}, status_code=500
            )
    except Exception as e:
        raise e

@router.get("/property/{cid}")
def get_container_property(req: Request, cid: int):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)
    user_token = req.cookies.get("user_token")
    cmd = f"select uid from \"User\" where user_token = '{user_token}'"
    uid = db.get_one_res(cmd)[0]
    cmd = f"select * from containers where uid = '{uid}' and cid={cid}"
    res = db.get_one_res(cmd)

    if res is None:
        message = "Current user is not accessible to this private container"
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)
    try:
        name, cpu, memory, portssh, portjupyter, porttsb, passwd, ip, cpu_name, gpu_type = container_property(db, cid)
        return JSONResponse(content={
            "status": 0,
            "name": name,
            "cpu": cpu,
            "memory": memory,
            "portssh": portssh,
            "portjupyter": portjupyter,
            "porttsb": porttsb,
            "passwd": passwd,
            "ip": ip,
            "cpu_name": cpu_name,
            "gpu_type": gpu_type
        })
    except Exception as e:
        raise e

@router.delete("/{cid}")
def delete_container(req:Request,cid:int):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)
    username = req.cookies.get("username")
    cmd = f"SELECT uid from \"User\" where name ='{username}'"
    uid = db.get_one_res(cmd)[0]

    try:
        status_code,status = container_rm(db,cid,uid)
        if status_code == -1:
            return JSONResponse(
                content={"status": -1, "error": status}, status_code=500
            )
        elif status_code == 0:
            return JSONResponse(content={"status": 0, "result": status})
        else:
            return JSONResponse(
                content={"status": -1, "error": "Unknown error"}, status_code=500
            )
    except Exception as e:
        raise e

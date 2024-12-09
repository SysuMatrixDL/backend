from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import your existing container_init handler
from common.connect import OpenGaussConnector
from controler.container_init import container_init
from config import *
from controler.container_status import container_status
from controler.container_start import container_start
from controler.container_stop import container_stop
from controler.container_rm import container_rm
from controler.get_properties import get_containers
import controler.user_valid as user_valid

router = APIRouter()


class CreateRequest(BaseModel):
    iid: int
    name: str
    cpu: int
    mem: int
    gid: Optional[int] = None


@router.post("")
def create_container(container_req: CreateRequest, req: Request):
    try:
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
            gid=container_req.gid,
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
    
    username = req.cookies.get("username")
    cmd = f"select uid from \"User\" where name = '{username}'"
    uid = db.get_one_res(cmd)[0]

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
                return JSONResponse(content={"status":-1,"error":status},status_code=500)
            elif status_code == 0:
                return JSONResponse(content={"status":0})
            else:
                raise Exception("Unkown status_code")
        elif update_req.cmd == "stop":
            status_code,status = container_stop(db,cid,uid)
            if status_code == -1:
                return JSONResponse(content={"status":-1,"error":status},status_code=500)
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


@router.get("/{cid}")
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

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from common.connect import OpenGaussConnector
from config import *
import controler.user_valid as user_valid
from controler.get_properties import get_user_images, image_property
from controler.image_create import image_create


router = APIRouter()


@router.get("")
def obtain_user_image(req: Request):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    username = req.cookies.get("username")
    cmd = f"select uid from \"User\" where name = '{username}'"
    uid = db.get_one_res(cmd)[0]

    ret = get_user_images(db, uid)
    ret = jsonable_encoder(ret)
    return JSONResponse(content=ret)


@router.get("/{iid}")
def obtain_image(req: Request, iid: int):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    ret = image_property(db, iid)
    ret = jsonable_encoder(ret)
    return JSONResponse(content=ret)


class CreateImageReq(BaseModel):
    cid: int
    name: str


@router.post("")
def create_image_from_container(req: Request, request: CreateImageReq):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    username = req.cookies.get("username")
    cmd = f"select uid from \"User\" where name = '{username}'"
    uid = db.get_one_res(cmd)[0]

    status,ret = image_create(db, request.cid, request.name, uid)
    if isinstance(ret,str):
        formatted_data = {
            "status":status,
            "error":ret
        }
    else:
        formatted_data = {
            "status":status,
            "iid":ret
        }
    formatted_data = jsonable_encoder(formatted_data)
    return JSONResponse(content=formatted_data)

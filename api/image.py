from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import *

from common.connect import OpenGaussConnector
import common.user_valid as user_valid

from controler.image_rm import image_rm
from controler.get_properties import get_device_images, get_public_images, get_user_images, image_property
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

    user_token = req.cookies.get("user_token")
    cmd = f"select uid from \"User\" where user_token = '{user_token}'"
    uid = db.get_one_res(cmd)[0]

    ret = get_user_images(db, uid)
    ret = jsonable_encoder(ret)
    return JSONResponse(content=ret)


@router.get("/public")
def obtain_public_image(req: Request):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    ret = get_public_images(db)
    ret = jsonable_encoder(ret)
    return JSONResponse(content=ret)


@router.get("/on/{did}")
def obtain_device_image(req: Request, did: int):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )

    user_token = req.cookies.get("user_token")
    cmd = f"select name from \"User\" where user_token = '{user_token}'"
    name = db.get_one_res(cmd)[0]

    ret = get_device_images(db, did, name)
    ret = jsonable_encoder(ret)
    return JSONResponse(content=ret)


@router.get("/property/{iid}")
def get_image_property(req: Request, iid: int):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    user_token = req.cookies.get("user_token")
    cmd = f"select uid from \"User\" where user_token = '{user_token}'"
    uid = db.get_one_res(cmd)[0]
    cmd = f"select * from user_images where uid = '{uid}' and iid={iid}"
    res = db.get_one_res(cmd)
    cmd = f"select public from images where iid = {iid}"
    public = db.get_one_res(cmd)[0]
    if res is None and public == 'f':
        message = "Current user is not accessible to this private image"
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    ret = image_property(db, iid)
    ret = jsonable_encoder(ret)
    return JSONResponse(content=ret)


class CreateImageReq(BaseModel):
    cid: int
    name: str
    public: bool


@router.post("/create")
def create_image_from_container(req: Request, request: CreateImageReq):
    print(request.public)
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    user_token = req.cookies.get("user_token")
    cmd = f"select uid from \"User\" where user_token = '{user_token}'"
    uid = db.get_one_res(cmd)[0]

    status,ret = image_create(db, request.cid, request.name, uid, request.public)
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


@router.post("/delete/{iid}")
def delete_container(req: Request, iid: int):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    user_token = req.cookies.get("user_token")
    cmd = f"select uid from \"User\" where user_token = '{user_token}'"
    uid = db.get_one_res(cmd)[0]
    cmd = f"select * from user_images where uid = '{uid}' and iid={iid}"
    res = db.get_one_res(cmd)
    cmd = f"select public from images where iid = {iid}"
    public = db.get_one_res(cmd)[0]
    if res is None and public == 'f':
        message = "Current user is not accessible to this private image"
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)
    
    status, message = image_rm(db, iid, uid)
    return JSONResponse(content={"status": status, "message": message})
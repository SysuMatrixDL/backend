from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from common.connect import OpenGaussConnector
from config import *
import controler.user_valid as user_valid
from controler.get_devices import get_devices
from controler.get_properties import device_property

router = APIRouter()


@router.get("")
def get_all_devices(req: Request):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    ret = get_devices(db)
    ret = jsonable_encoder(ret)
    return JSONResponse(content=ret)


@router.get("/{did}")
def get_did_devices(req: Request, did: int):
    db = OpenGaussConnector(
        host=DB_IP, port=DB_PORT, user=DB_USER, pwd=DB_PWD, database=DB_CONNECT_DB
    )
    status, message = user_valid.user_exists(db, req)
    if status == False:
        return JSONResponse(content={"status": -1, "error": message}, status_code=401)

    ret_data = device_property(db, did)

    # Transform the list into a dictionary with named fields
    formatted_data = {
        "total_cpu": ret_data[0],
        "used_cpu": ret_data[1],
        "cpu_name": ret_data[2],
        "total_memory": ret_data[3],
        "used_memory": ret_data[4],
        "gpus": [{"gid": gpu[0], "name": gpu[1]} for gpu in ret_data[5]],
        "gpu_used": ret_data[6],
        "images": ret_data[7]  # This is already in the correct format
    }
    ret = jsonable_encoder(formatted_data)
    return JSONResponse(content=ret)

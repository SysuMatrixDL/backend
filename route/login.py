from fastapi import APIRouter, Request, Response,HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from controler.connect import OpenGaussConnector
from controler.hash_pwd import generate_user_token,generate_sha256_digest
router = APIRouter()

class UserLogin(BaseModel):
    username: str
    password: str
    
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

@router.post("/login")
def login(user: UserLogin,req:Request):
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='postgres', pwd='OGSql@123', database='postgres')
    try:
        user.password = generate_sha256_digest(user.password)
        cmd = f"SELECT uid, name, email, usage FROM \"User\" WHERE name = '{user.username}' AND password = '{user.password}';"
        res = db.get_one_res(cmd)
        if res is None:
            return JSONResponse(content={"error": "Invalid username or password"}, status_code=401)

        user_token = generate_user_token(user.password)
        # Update the user_token in the database
        cmd = "UPDATE \"User\" SET user_token = '{0}' WHERE uid = {1};".format(user_token,res[0])
        db.exec(cmd)

        json_resp = JSONResponse(content={"message":"{0} logged in successfully".format(user.username)})
        json_resp.set_cookie(key="username",value=user.username)
        json_resp.set_cookie(key="user_token", value=user_token)
        return json_resp
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/logout")
def logout(req:Request):
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='postgres', pwd='OGSql@123', database='postgres')
    try:
        username = req.cookies.get("username")
        user_token = req.cookies.get("user_token")
        if username is None or user_token is None:
            return JSONResponse(content={"error": "Empty username or user_token"}, status_code=401)
        cmd = "SELECT COUNT(*) FROM \"User\" WHERE name='{0}' AND user_token='{1}'".format(username,user_token)
        res = db.get_one_res(cmd)
        if res is None:
            return JSONResponse(content={"error": "Invalid username or password"}, status_code=401)
        # Update the user_token to NULL in the database
        cmd = "UPDATE \"User\" SET user_token = NULL WHERE name = '{}' AND user_token = '{}';".format(username, user_token)
        db.exec(cmd)

        # Clear the cookies
        response = JSONResponse(content={"message": "{0} logged out successfully".format(username)})    
        response.delete_cookie(key="username")
        response.delete_cookie(key="user_token")
        return response
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/register")
def register(user: UserRegister):
    db = OpenGaussConnector(ip='127.0.0.1', port=5432, user='postgres', pwd='OGSql@123', database='postgres')
    try:
        # Check if the username or email already exists
        cmd = f"SELECT COUNT(*) FROM \"User\" WHERE name = '{user.username}' OR email = '{user.email}';"
        res = db.get_one_res(cmd)
        if res[0] > 0:
            raise HTTPException(status_code=401,detail="Username or email already exists")
        
        # Get the next available uid
        cmd = "SELECT COALESCE(MAX(uid), 0) + 1 FROM \"User\";"
        new_uid = db.get_one_res(cmd)[0]
        
        user.password = generate_sha256_digest(user.password)

        # Insert the new user into the database
        cmd = f"INSERT INTO \"User\" (uid, name, email, password, usage,user_token) VALUES ({new_uid}, '{user.username}', '{user.email}', '{user.password}', 0,NULL);"
        db.exec(cmd)

        json_resp = JSONResponse(content={"message": "User {0} registered successfully".format(user.username)})
        return json_resp
    except Exception as e:
        if type(e) == HTTPException:
            return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
        return JSONResponse(content={"error": str(e)}, status_code=500)


from fastapi import Request
from common.connect import OpenGaussConnector

def user_exists(db:OpenGaussConnector, req:Request)-> tuple[bool, str] :
    """
    验证用户是否存在
    """
    username = req.cookies.get("username")
    user_token = req.cookies.get("user_token")
    if(username is None or user_token is None):
        return (False, "Cookies are not set")
    cmd = f"select count(*) from \"User\" where name = '{username}' and user_token IS NOT NULL and user_token = '{user_token}' "
    res = db.exec(cmd)
    if len(res) == 0:
        return False, "User does not log in or exist"
    else:
        return True, "User is verified"
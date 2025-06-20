# standard library
import jwt
import datetime
from typing import Annotated
from fastapi import APIRouter, Body, HTTPException
# local library
from weelink.core.internal.config import conf
from weelink.dashboard.constants import SECRET_KEY, ALGORITHM

router = APIRouter()


@router.post("/login")
async def login_api(
    username: Annotated[str, Body()],
    password: Annotated[str, Body()]
):
    if not (username == conf.DASHBOARD_USERNAME and \
            password == conf.DASHBOARD_PASSWORD):
        return HTTPException(status_code=401, detail="账号密码不匹配!")
    
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
    }
    return {
        "token": jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM),
        "username": username
    }

@router.post("/reset-pwd")
async def reset_pwd_api(
    current_password: Annotated[str, Body()],
    new_password: Annotated[str, Body()]
):
    if not current_password == conf.DASHBOARD_PASSWORD:
        return HTTPException(status_code=401, detail="密码错误!")
    
    if not new_password:
        return HTTPException(status_code=500, detail="新密码不允许为空!")
    conf.DASHBOARD_PASSWORD = new_password
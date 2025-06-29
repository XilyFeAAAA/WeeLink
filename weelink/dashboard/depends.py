# standard library
import jwt
import datetime
from fastapi import Request, HTTPException

# local library
from weelink.core.internal.config import conf
from weelink.core.linkhub import Linkhub
from weelink.dashboard.constants import SECRET_KEY, ALGORITHM

async def login_required(request: Request) -> str:
    """判断是否登录的依赖"""
    auth = request.headers.get("Authorization")
    token = auth.removeprefix("Bearer")
    if token is None:
        raise HTTPException(status_code=401, detail="请求未附带Token,请重新登录!")
    token = token.strip()
    try:
        payload: dict = jwt.decode(
            token, SECRET_KEY, algorithms=ALGORITHM
        )
        if (usrname := payload.get("username")) != conf["DASHBOARD_USERNAME"]:
            raise HTTPException(status_code=401, detail="JWT解析错误,请重新登录!")
        
        dt = datetime.datetime.utcnow().timestamp()
        if (expired_time := payload.get("exp")) and int(dt) > expired_time:
            raise HTTPException(status_code=401, detail="Token已过期,请重新登录!")
        
        return usrname
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token解析失败,请重新登录!")


async def get_linkhub(request: Request) -> Linkhub:
    """获取linkhub实例的依赖"""
    return request.app.state.linkhub
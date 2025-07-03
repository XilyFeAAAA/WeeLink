# standard library
from typing import Annotated
from fastapi import APIRouter, Depends, Body, Query, HTTPException

# local library
from weelink.core.utils import logger
from weelink.core.internal.config import conf
from weelink.dashboard.depends import login_required, get_linkhub


router = APIRouter()


@router.get("/", dependencies=[Depends(login_required)])
async def config_get_api():
    return {
        "scheme": conf.scheme,
        "data": {
            key: value for key, value in conf.items() if key in conf["SCHEME_KEYS"]
        },
    }


@router.post("/update", dependencies=[Depends(login_required)])
async def config_update_api(config: Annotated[dict, Body(embed=True)]):
    backup = None
    try:
        if not config:
            return HTTPException(status_code=400, detail="配置项不能为空")

        # 验证配置
        for key in config.copy():
            if key not in conf["SCHEME_KEYS"]:
                del config[key]

        backup = conf.copy()
        conf.update(config)
        conf.save()
        return logger.info("配置项已更新")
    except Exception as e:
        if backup is not None:
            conf.update(backup)
            conf.save()
        return HTTPException(status_code=500, detail=f"保存配置项错误: {e}")

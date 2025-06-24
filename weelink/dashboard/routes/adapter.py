# standard library
from typing import Annotated
from fastapi import APIRouter, Query, Depends, HTTPException
# local library
from weelink.core.linkhub import Linkhub
from weelink.core.internal.config import conf
from weelink.dashboard.depends import login_required, get_linkhub

router = APIRouter()


@router.get("/", dependencies=[Depends(login_required)])
async def adapter_get_api(
    adapter_id: Annotated[str, Query()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    if (adapter := linkhub.adapter.get_adapter(adapter_id)) is None:
        raise HTTPException(status_code=500, detail="适配器ID错误")
    return {
        "adapter": {
            "id": adapter.id,
            "name": adapter.name,
            "desc": adapter.desc,
            "platform": adapter.wechat_platform,
            "version": adapter.wechat_version,
            "fields": adapter.get_fields()
        }
    }


@router.get("/docs", dependencies=[Depends(login_required)])
async def adapter_docs_api(
    adapter_id: Annotated[str, Query()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    if (adapter := linkhub.adapter.get_adapter(adapter_id)) is None:
        raise HTTPException(status_code=500, detail="适配器ID错误")
    return {
        "docs": adapter.cls.docs()
    }



@router.get("/list", dependencies=[Depends(login_required)])
async def adapter_list_api(linkhub: Annotated[Linkhub, Depends(get_linkhub)]):
    return {
        "adapters": [{
            "id": adapter.id,
            "name": adapter.name,
            "desc": adapter.desc,
            "platform": adapter.wechat_platform,
            "version": adapter.wechat_version
        } for adapter in linkhub.adapter.get_all_adapters()]
    }

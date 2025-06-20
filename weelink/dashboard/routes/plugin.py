# standard library
from typing import Annotated
from fastapi import APIRouter, Query, Depends, HTTPException

# local library
from weelink.core.linkhub import Linkhub
from weelink.core.internal.config import conf
from weelink.dashboard.depends import login_required, get_linkhub

router = APIRouter()


@router.get("/list", dependencies=[Depends(login_required)])
async def plugin_list_api(linkhub: Annotated[Linkhub, Depends(get_linkhub)]):
    return {
        "plugins": [{
            "name": plugin.name,
            "enable": plugin.enable,
            "author": plugin.author,
            "version": plugin.version,
            "desc": plugin.desc,
            "repo": plugin.repo
        } for plugin in linkhub.plugin.get_all_plugins()]
    }
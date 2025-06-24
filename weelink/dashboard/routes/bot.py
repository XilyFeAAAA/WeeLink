# standard library
from typing import Annotated
from fastapi import APIRouter, Depends, Body, Query
# local library
from weelink.core.linkhub import Linkhub
from weelink.core.adapter import BotConfig
from weelink.dashboard.depends import login_required, get_linkhub


router = APIRouter()


@router.get("/list", dependencies=[Depends(login_required)])
async def bot_list_api(linkhub: Annotated[Linkhub, Depends(get_linkhub)]):
    return {
        "bots": [{
            "id": bot_doc.id,
            "state": bot_doc.state,
            "adapter": bot_doc.adapter_metadata.name,
            "alias": bot_doc.alias,
            "desc": bot_doc.desc
        } for bot_doc in linkhub.adapter.get_all_bots()] 
    }


@router.post("/add", dependencies=[Depends(login_required)])
async def bot_add_api(
    bot: Annotated[BotConfig, Body()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    return await linkhub.adapter.add_bot(bot_config=bot)


@router.post("/del", dependencies=[Depends(login_required)])
async def bot_del_api(
    bot_id: Annotated[str, Query()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    return await linkhub.adapter.delete_bot(bot_id)


@router.post("/switch", dependencies=[Depends(login_required)])
async def bot_switch_api(
    bot_id: Annotated[str, Body()],
    state: Annotated[bool, Body()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    return await linkhub.adapter.start_bot(bot_id) if state \
        else await linkhub.adapter.stop_bot(bot_id)
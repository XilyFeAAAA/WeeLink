# standard library
from typing import Annotated
from fastapi import APIRouter, Query, Depends, HTTPException, Request
# local library
from weelink.core.linkhub import Linkhub
from weelink.core.internal.config import conf
from weelink.dashboard.depends import login_required, get_linkhub

router = APIRouter()


@router.post("/restart", dependencies=[Depends(login_required)])
async def restart_linkhub_api(
    request: Request,
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    if not hasattr(request.app.state, "initiator"):
        raise HTTPException(status_code=500, detail="无法访问 Initiator 实例")
    
    initiator = request.app.state.initiator
    return await initiator.restart_linkhub()
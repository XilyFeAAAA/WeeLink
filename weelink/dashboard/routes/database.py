# standard library
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query
# local library
from weelink.core.linkhub import Linkhub
from weelink.core.internal.db import MessageRepository
from weelink.dashboard.depends import login_required, get_linkhub


router = APIRouter()


@router.get("/mongodb")
async def mongodb_api(
    page: Annotated[int, Query()],
    limit: Annotated[int, Query()],
    adapter_name: Annotated[str|None, Query()] = None,
    source: Annotated[Literal["chatroom", "friend"]|None, Query()] = None,
    content: Annotated[str|None, Query()] = None,
):
    return {
        "mongodb": await MessageRepository.find_messages(
            page, limit, adapter_name, source, content
        )
    }
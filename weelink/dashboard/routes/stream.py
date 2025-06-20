# standard library
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

# local library
from weelink.dashboard.depends import login_required
from weelink.core.utils.logger import logger
from weelink.core.utils.sse import sse_manager


router = APIRouter()


@router.get("/", dependencies=[Depends(login_required)])
async def sse_api():
    
    async def event_stream():
        try:
            async for message in sse_manager.stream():
                yield message
        except Exception as e:
            logger.error(f"SSE流异常: {e}")
            yield sse_manager._format_sse_message("error", {
                "message": "连接异常"
            })
        
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
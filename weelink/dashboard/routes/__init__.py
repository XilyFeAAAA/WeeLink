# standard library
from fastapi import APIRouter

# local library
from .auth import router as auth_router
from .bot import router as bot_router
from .adapter import router as adapter_router
from .plugin import router as plugin_router
from .stream import router as stream_router
from .system import router as system_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(bot_router, prefix="/bot", tags=["bot"])
api_router.include_router(adapter_router, prefix="/adapter", tags=["adapter"])
api_router.include_router(plugin_router, prefix="/plugin", tags=["plugin"])
api_router.include_router(stream_router, prefix="/stream", tags=["stream"])
api_router.include_router(system_router, prefix="/system", tags=["system"])
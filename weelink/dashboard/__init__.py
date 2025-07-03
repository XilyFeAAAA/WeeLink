# standard library
import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
# local library
from .routes import api_router
from weelink.core.linkhub import Linkhub
from weelink.core.utils import logger
from weelink.core.internal.config import conf


# ----- Middleware -----
middlewares = [
    Middleware(
        CORSMiddleware,
        allow_origins=conf["BACKEND_CORS_ORIGINS"],
        allow_credentials=conf["BACKEND_CORS_CREDENTIALS"],
        allow_methods=conf["BACKEND_CORS_METHODS"],
        allow_headers=conf["BACKEND_CORS_HEADERS"]
    )
]


class Dashboard:
    
    def __init__(self, linkhub: Linkhub, initiator=None) -> None:
        self.app = FastAPI(
            title="WeeLink WebUI",
            openapi_url="/openapi.json",
            middleware=middlewares
        )
        self.app.include_router(api_router, prefix="/api")
        self.app.state.linkhub = linkhub
        self.server = None
        
        # 存储 initiator 实例的引用，用于重启 linkhub
        if initiator:
            self.app.state.initiator = initiator
    
    
    async def start(self) -> None:       
        # 开启服务
        self.server = uvicorn.Server(
            config=uvicorn.Config(
                app=self.app,
                host=conf["DASHBOARD_HOST"],
                port=conf["DASHBOARD_PORT"],
                log_config=None
            )
        )
        try:
            logger.info(f"WeeLink WebUI 已启动, 可访问 ➜  http://{conf['DASHBOARD_HOST']}:{conf['DASHBOARD_PORT']}")
            logger.info(f"WeeLink WebUI 接口文档可访问 ➜  http://{conf['DASHBOARD_HOST']}:{conf['DASHBOARD_PORT']}/docs")
            await self.server.serve()
        except asyncio.CancelledError:
            print("WeeLink WebUI已关闭")
    
    async def stop(self):
        """停止服务"""
        await self.server.shutdown()

# -*- coding: utf-8 -*-
"""
应用入口文件模板
位置: backend/main.py

这是标准的FastAPI应用入口文件，包含应用创建、生命周期管理、路由注册等
"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.corelibs.logger import init_logger, logger
from app.db import redis_pool
from app.init.cors import init_cors
from app.init.exception import init_exception
from app.init.middleware import init_middleware
from app.init.routers import init_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动逻辑
    redis_pool.init_by_config(config=settings)
    init_logger()
    
    yield  # 分隔启动和关闭逻辑
    
    # 关闭逻辑
    try:
        if hasattr(redis_pool, 'redis') and redis_pool.redis:
            await redis_pool.redis.aclose()
            logger.info("Redis连接已关闭")
    except Exception as e:
        logger.error(f"关闭Redis连接时出错: {e}")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app: FastAPI = FastAPI(
        title="ai_quote",
        description=settings.APP_DESC,
        version=settings.APP_VERSION,
        lifespan=lifespan
    )
    init_exception(app)  # 注册捕获全局异常
    init_router(app)  # 注册路由
    # init_middleware(app)  # 注册请求响应拦截（可选）
    init_cors(app)  # 初始化跨域

    return app


app = create_app()

# gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8101
if __name__ == '__main__':  
    uvicorn.run(app='main:app', host="0.0.0.0", port=8000, reload=True)


def custom_openapi():
    """自定义OpenAPI文档"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="Your API description",
        routes=app.routes,
    )
    
    # 添加安全模式
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "token"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer"
        }
    }
    
    # 应用安全要求
    openapi_schema["security"] = [
        {
            "ApiKeyAuth": [],
            "BearerAuth": []
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

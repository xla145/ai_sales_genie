# -*- coding: utf-8 -*-
"""
API依赖注入模块
生成代码时可以直接导入使用: from app.api.deps import get_db, get_redis
"""
import typing

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from app.db.redis import MyAsyncRedis
from app.db.sqlalchemy import async_session


async def get_db() -> typing.AsyncGenerator[AsyncSession, None]:
    """数据库连接会话依赖"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis(request: Request) -> MyAsyncRedis:
    """Redis连接对象依赖"""
    return await request.app.state.redis

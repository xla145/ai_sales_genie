# -*- coding: utf-8 -*-
"""
数据库连接模块
生成代码时可以直接导入使用: from app.db.sqlalchemy import async_session, async_transaction
"""
import asyncio
import functools
import traceback
import typing
from asyncio import current_task
from contextlib import asynccontextmanager

from app.corelibs.logger import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.utils.context import SQLAlchemySession
from app.config import settings

# 创建数据库引擎
engine = create_async_engine(
    url=settings.DATABASE_URL,  # 数据库uri
    echo=settings.DEBUG,  # 是否打印日志
    poolclass=NullPool,  # 使用 NullPool 避免连接池在多进程/多线程间共享问题
)

# 操作表会话
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False  # 防止提交后属性过期
)

async_session = async_scoped_session(async_session_factory, scopefunc=current_task)


def provide_session(func: typing.Callable):
    """
    提供数据库会话的装饰器
    :param func: 函数
    :return:
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        arg_session = 'session'

        func_params = func.__code__.co_varnames
        session_in_args = arg_session in func_params and func_params.index(arg_session) < len(args)
        session_in_kwargs = arg_session in kwargs

        if session_in_kwargs or session_in_args:
            return await func(*args, **kwargs)
        else:
            async with async_session() as session:
                fs = functools.partial(func, session=session, *args, **kwargs)
                try:
                    return await fs()
                except IntegrityError:
                    logger.error(traceback.format_exc())
                    await session.rollback()
                    raise
                except Exception:
                    await session.rollback()
                    raise

    return wrapper


@asynccontextmanager
async def content_transaction():
    """事务上下文管理器"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


def async_transaction(func):
    """
    异步事务装饰器
    自动管理数据库事务，确保操作的一致性
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # 检查是否已经有会话（例如在调度器线程中已设置的会话）
        existing_session = SQLAlchemySession.get()
        if existing_session is not None:
            # 如果已有会话，直接使用，不创建新会话
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        else:
            # 如果没有会话，创建新会话
            async with content_transaction() as session:
                token = SQLAlchemySession.set(session)
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                finally:
                    SQLAlchemySession.reset(token)

    return wrapper

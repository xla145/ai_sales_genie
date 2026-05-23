"""
公共模块
包含所有可直接使用的公共模块代码

目录结构：
- db.py: 数据库连接模块
- redis.py: Redis连接模块
- config.py: 配置模块
- deps.py: API依赖注入
- exceptions.py: 异常类定义
- api_router.py: API路由聚合模块
- corelibs.py: 核心库说明（custom_router, logger, codes等）
- init_modules.py: 初始化模块说明（routers, exception, cors等）
- utils.py: 工具函数说明（response, context, serialize等）
- schemas.py: Schema基础类
- main.py: 应用入口文件模板
- base_model_usage.md: Base模型使用指南（包含所有CRUD方法说明）

使用方式：
# 数据库连接
from app.db.sqlalchemy import async_session, async_transaction

# Redis连接
from app.db.redis import redis_pool

# 配置
from app.config import settings

# API依赖
from app.api.deps import get_db, get_redis

# 异常处理
from app.exceptions.exceptions import BusinessException, IdNotExist

# 路由
from app.corelibs.custom_router import APIRouter

# 响应
from app.utils.response import HttpResponse

# Schema基础类
from app.schemas.common import BaseSchema

# Base模型
from app.models.base import Base
"""

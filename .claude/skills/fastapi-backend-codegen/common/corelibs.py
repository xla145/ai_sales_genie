# -*- coding: utf-8 -*-
"""
核心库模块
包含custom_router, logger, codes等公共模块
"""

# ==================== custom_router.py ====================
"""
自定义路由模块
位置: app/corelibs/custom_router.py

使用方式:
from app.corelibs.custom_router import APIRouter

router = APIRouter()  # 自动设置请求上下文
"""

# ==================== logger.py ====================
"""
日志模块
位置: app/corelibs/logger.py

使用方式:
from app.corelibs.logger import logger, init_logger

# 记录日志
logger.info("信息")
logger.warning("警告")
logger.error("错误")

# 初始化日志（在应用启动时调用）
init_logger()
"""

# ==================== codes.py ====================
"""
状态码定义模块
位置: app/corelibs/codes.py

使用方式:
from app.corelibs.codes import CodeEnum

# 使用状态码
code = CodeEnum.PARTNER_CODE_OK.code  # 0
msg = CodeEnum.PARTNER_CODE_OK.msg    # "OK"
"""

# ==================== local.py ====================
"""
本地上下文变量模块
位置: app/corelibs/local.py

使用方式:
from app.corelibs.local import g

# 设置和获取上下文变量
g.trace_id = "xxx"
trace_id = g.trace_id
"""

# ==================== consts.py ====================
"""
常量定义模块
位置: app/corelibs/consts.py

包含:
- 分页常量: DEFAULT_PAGE, DEFAULT_PER_PAGE
- 缓存时间常量: CACHE_MINUTE, CACHE_HOUR, CACHE_DAY等
- 缓存键模板: TEST_USER_INFO等

使用方式:
from app.corelibs.consts import DEFAULT_PAGE, CACHE_HOUR
"""

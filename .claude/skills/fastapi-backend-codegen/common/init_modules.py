# -*- coding: utf-8 -*-
"""
应用初始化模块
包含routers, exception, cors, middleware等初始化函数
"""

# ==================== routers.py ====================
"""
路由初始化模块
位置: app/init/routers.py

使用方式:
from app.init.routers import init_router

# 在create_app中调用
init_router(app)  # 注册所有路由
"""

# ==================== exception.py ====================
"""
异常处理初始化模块
位置: app/init/exception.py

使用方式:
from app.init.exception import init_exception

# 在create_app中调用
init_exception(app)  # 注册全局异常处理器
"""

# ==================== cors.py ====================
"""
CORS初始化模块
位置: app/init/cors.py

使用方式:
from app.init.cors import init_cors

# 在create_app中调用
init_cors(app)  # 初始化跨域配置
"""

# ==================== middleware.py ====================
"""
中间件初始化模块
位置: app/init/middleware.py

使用方式:
from app.init.middleware import init_middleware

# 在create_app中调用（可选）
init_middleware(app)  # 注册请求响应拦截中间件
"""

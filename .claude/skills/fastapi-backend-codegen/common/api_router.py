# -*- coding: utf-8 -*-
"""
API路由聚合模块
位置: app/api/api_router.py

将所有API路由聚合到一个router中
"""
from fastapi import APIRouter
from app.api.v1 import projects, features, analysis, quotes, configs, files, system_configs
from app.config import settings

router = APIRouter()

# 注册所有路由
router.include_router(projects.router, tags=["项目"])
router.include_router(features.router, tags=["功能点"])
router.include_router(analysis.router, tags=["分析"])
router.include_router(quotes.router, tags=["报价"])
router.include_router(configs.router, tags=["配置"])
router.include_router(system_configs.router, tags=["系统配置"])
router.include_router(files.router, tags=["文件"])

# 使用方式：
# 在 app/init/routers.py 中：
# from app.api.api_router import router
# app.include_router(router, prefix=settings.API_V1_PREFIX)

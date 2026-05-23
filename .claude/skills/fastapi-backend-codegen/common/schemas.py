# -*- coding: utf-8 -*-
"""
Schema公共模块
包含BaseSchema等基础Schema类
"""
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PageResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    total: int
    page: int
    page_size: int
    items: List[T]


class BaseSchema(BaseModel):
    """基础Schema - 所有Schema应继承此类"""
    class Config:
        from_attributes = True  # 支持ORM对象转换
        json_encoders = {
            # 可以添加自定义编码器
        }

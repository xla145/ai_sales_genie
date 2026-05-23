"""
{ModelName}Schema模板
复制此模板并替换 {ModelName} 等占位符
"""
from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema


class {ModelName}Base(BaseSchema):
    """{ModelName}基础Schema"""
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    # 添加更多基础字段...


class {ModelName}Create({ModelName}Base):
    """创建{ModelName}Schema"""
    pass


class {ModelName}Update(BaseSchema):
    """更新{ModelName}Schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    # 添加更多可更新字段...


class {ModelName}({ModelName}Base):
    """{ModelName}响应Schema"""
    id: int
    creation_date: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    updation_date: datetime

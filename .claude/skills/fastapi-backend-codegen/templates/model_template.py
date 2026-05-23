"""
{ModelName}模型模板
复制此模板并替换 {ModelName}、{table_name} 等占位符
"""
from sqlalchemy import Column, BigInteger, String, Text, Index, Integer, Boolean, DECIMAL, JSON, DateTime
from sqlalchemy import select, and_
from app.models.base import Base
from app.corelibs.logger import logger


class {ModelName}(Base):
    """{表名}表"""
    __tablename__ = "{table_name}"
    
    # 业务字段定义
    name = Column(String(255), nullable=False, comment="名称")
    description = Column(Text, comment="描述")
    status = Column(String(50), default="active", nullable=False, comment="状态")
    # 添加更多业务字段...
    
    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_name", "name"),
        # 添加更多索引...
        {"comment": "{表名}表"}
    )
    
    def __repr__(self):
        return f"<{ModelName}(id={self.id}, name={self.name})>"
    
    @classmethod
    async def get_by_status(cls, status: str):
        """按状态查询列表"""
        query_conditions = [
            cls.enabled_flag == 1,  # 必须包含此条件
            cls.status == status
        ]
        stmt = select(*cls.get_table_columns()).where(and_(*query_conditions))
        return await cls.get_result(stmt)
    
    @classmethod
    async def get_data_with_pagination(cls, status: str = None, name: str = None):
        """分页查询"""
        query_conditions = [cls.enabled_flag == 1]  # 必须包含此条件
        if status:
            query_conditions.append(cls.status == status)
        if name:
            query_conditions.append(cls.name.like(f"%{name}%"))
        stmt = select(*cls.get_table_columns()).where(and_(*query_conditions)).order_by(cls.creation_date.desc())
        return await cls.pagination(stmt)
    
    # 添加更多自定义查询方法...

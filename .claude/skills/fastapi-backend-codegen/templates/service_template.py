"""
{ModelName}服务模板
复制此模板并替换 {ModelName}、{model_name} 等占位符
"""
from app.models.{model_file} import {ModelName} as {ModelName}Model
from app.schemas.{schema_file} import {ModelName}Create, {ModelName}Update
from app.corelibs.logger import logger
from app.exceptions.exceptions import IdNotExist, BusinessException


class {ModelName}Service:
    """{ModelName}服务类"""
    
    @staticmethod
    async def create_{model_name}(data: {ModelName}Create):
        """创建{ModelName}"""
        # 业务验证（可选）
        # if await {ModelName}Model.exists_by_name(data.name):
        #     raise BusinessException("{ModelName}名称已存在")
        
        # 调用Model层
        db_obj = await {ModelName}Model.create(data.model_dump())
        return db_obj
    
    @staticmethod
    async def get_{model_name}({model_name}_id: int):
        """获取{ModelName}详情"""
        result = await {ModelName}Model.get({model_name}_id)
        if not result:
            raise IdNotExist()
        return result
    
    @staticmethod
    async def page_{model_name}s(status: str = None, name: str = None):
        """分页查询{ModelName}列表"""
        # 调用Model层
        data = await {ModelName}Model.get_data_with_pagination(status=status, name=name)
        return data
    
    @staticmethod
    async def update_{model_name}({model_name}_id: int, data: {ModelName}Update):
        """更新{ModelName}"""
        # 更新数据
        update_params = data.model_dump()
        result = await {ModelName}Model.update({model_name}_id, update_params)
        return result
    
    @staticmethod
    async def delete_{model_name}({model_name}_id: int):
        """删除{ModelName}（软删除）"""
        count = await {ModelName}Model.delete({model_name}_id)
        if count == 0:
            raise IdNotExist()
        return count

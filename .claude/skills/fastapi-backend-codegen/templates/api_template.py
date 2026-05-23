"""
{ModelName}管理API模板
复制此模板并替换 {ModelName}、{model_name}、{api_prefix} 等占位符
"""
from typing import Optional
from app.schemas.{schema_file} import {ModelName}, {ModelName}Create, {ModelName}Update
from app.models.{model_file} import {ModelName} as {ModelName}Model
from app.corelibs.custom_router import APIRouter
from app.services.{service_file} import {ModelName}Service
from app.utils.response import HttpResponse

router = APIRouter()


@router.post("/{api_prefix}", response_model={ModelName}, status_code=201)
async def create_{model_name}(data: {ModelName}Create):
    """创建{ModelName}"""
    db_obj = await {ModelName}Service.create_{model_name}(data)
    return await HttpResponse.success(data=db_obj)


@router.get("/{api_prefix}")
async def get_{model_name}s(
    status: Optional[str] = None,
    name: Optional[str] = None,
):
    """获取{ModelName}列表"""
    data = await {ModelName}Service.page_{model_name}s(status=status, name=name)
    return await HttpResponse.success(data=data)


@router.get("/{api_prefix}/{{id}}", response_model={ModelName})
async def get_{model_name}(id: int):
    """获取{ModelName}详情"""
    obj = await {ModelName}Service.get_{model_name}(id)
    return await HttpResponse.success(data=obj)


@router.put("/{api_prefix}/{{id}}", response_model={ModelName})
async def update_{model_name}(
    id: int,
    data: {ModelName}Update,
):
    """更新{ModelName}"""
    obj = await {ModelName}Service.update_{model_name}(id, data)
    return await HttpResponse.success(data=obj)


@router.delete("/{api_prefix}/{{id}}", status_code=204)
async def delete_{model_name}(id: int):
    """删除{ModelName}"""
    await {ModelName}Service.delete_{model_name}(id)
    return await HttpResponse.success()

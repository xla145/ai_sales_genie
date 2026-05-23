"""
异常处理参考文档
使用自定义异常类，会被全局异常处理器自动捕获
"""
# 异常类位置: app/exceptions/exceptions.py

from app.exceptions.exceptions import (
    BusinessException,
    ValidationException,
    IdNotExist,
    ParameterError,
    SystemException,
    DatabaseException,
    AuthenticationException,
    AuthorizationException
)

# ==================== 常用异常 ====================

# 业务异常
"""
raise BusinessException("业务逻辑错误")
raise BusinessException("项目名称已存在")
"""

# 验证异常
"""
raise ValidationException("数据验证失败")
raise ValidationException("必填字段不能为空")
"""

# ID不存在
"""
raise IdNotExist()  # 自动返回"查询id不存在"消息
"""

# 参数错误
"""
raise ParameterError("参数不能为空")
raise ParameterError("参数格式错误")
"""

# 系统异常
"""
raise SystemException("系统异常，请联系管理员")
raise SystemException("未知错误", code=500)
"""

# 数据库异常
"""
raise DatabaseException("数据库操作异常")
"""

# 认证异常
"""
raise AuthenticationException("认证失败")
"""

# 授权异常
"""
raise AuthorizationException("权限不足")
"""

# ==================== 异常处理流程 ====================
"""
1. 在Service层抛出异常
2. 全局异常处理器自动捕获
3. 返回统一格式的响应
4. 记录详细日志

不需要在每个API中try-catch，异常会自动处理
"""

# ==================== 使用示例 ====================
"""
# Service层
async def get_project(project_id: int):
    result = await Project.get(project_id)
    if not result:
        raise IdNotExist()  # 自动返回404响应
    return result

async def create_project(data: ProjectCreate):
    if await Project.exists_by_name(data.name):
        raise BusinessException("项目名称已存在")  # 自动返回400响应
    return await Project.create(data.model_dump())
"""

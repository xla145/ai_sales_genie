# -*- coding: utf-8 -*-
"""
工具函数模块
包含response, context, serialize, common等工具模块
"""

# ==================== response.py ====================
"""
响应工具模块
位置: app/utils/response.py

使用方式:
from app.utils.response import HttpResponse

# 成功响应
return await HttpResponse.success(data={"id": 1}, msg="操作成功")

# 失败响应
return await HttpResponse.fail(code=-1, msg="操作失败")
"""

# ==================== context.py ====================
"""
上下文管理模块
位置: app/utils/context.py

使用方式:
from app.utils.context import AppTraceId, SQLAlchemySession, FastApiRequest

# 获取追踪ID
trace_id = AppTraceId.get()

# 获取数据库会话
session = SQLAlchemySession.get()

# 获取请求对象
request = FastApiRequest.get()
"""

# ==================== serialize.py ====================
"""
序列化工具模块
位置: app/utils/serialize.py

使用方式:
from app.utils.serialize import default_serialize

# 序列化对象
serialized = default_serialize(obj)
"""

# ==================== common.py ====================
"""
通用工具函数模块
位置: app/utils/common.py

使用方式:
from app.utils.common import get_str_uuid, md5_encrypt, is_empty_string

# 生成UUID
uuid_str = get_str_uuid()

# MD5加密
encrypted = md5_encrypt("password")

# 判断空字符串
if is_empty_string(data):
    raise ParameterError("数据不能为空")
"""

# ==================== current_user.py ====================
"""
当前用户工具模块
位置: app/utils/current_user.py

使用方式:
from app.utils.current_user import get_user_id, current_user

# 获取当前用户ID
user_id = await get_user_id()

# 获取当前用户信息
user_info = await current_user(token)
"""

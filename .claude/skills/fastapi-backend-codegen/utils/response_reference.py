"""
响应工具参考文档
使用HttpResponse类统一返回响应
"""
# 响应工具位置: app/utils/response.py

from app.utils.response import HttpResponse

# ==================== 成功响应 ====================
"""
# 基础成功响应
return await HttpResponse.success(
    data={"id": 1, "name": "test"},
    msg="操作成功"
)

# 只返回数据
return await HttpResponse.success(data={"id": 1})

# 自定义状态码和消息
return await HttpResponse.success(
    data={"id": 1},
    code=0,
    msg="创建成功"
)
"""

# ==================== 失败响应 ====================
"""
# 基础失败响应
return await HttpResponse.fail(
    code=-1,
    msg="操作失败"
)

# 带数据的失败响应
return await HttpResponse.fail(
    code=-1,
    msg="操作失败",
    data={"error": "详细错误信息"}
)
"""

# ==================== HTTP状态码响应 ====================
"""
# 400 Bad Request
return await HttpResponse.resp_400(msg="请求错误")

# 401 Unauthorized
return await HttpResponse.resp_401(msg="未授权，请重新登录")

# 403 Forbidden
return await HttpResponse.resp_403(msg="拒绝访问")

# 404 Not Found
return await HttpResponse.resp_404(msg="资源不存在")

# 422 Unprocessable Entity
return await HttpResponse.resp_422(msg="参数验证失败")

# 500 Internal Server Error
return await HttpResponse.resp_500(msg="服务器错误")
"""

# ==================== 响应格式 ====================
"""
所有响应统一格式：
{
    "code": 0,           # 业务状态码
    "msg": "OK",         # 消息
    "data": {},          # 数据
    "success": true,     # 是否成功
    "trace_id": "xxx"    # 追踪ID
}
"""

# ==================== 使用状态码枚举 ====================
"""
from app.corelibs.codes import CodeEnum

return await HttpResponse.success(
    code=CodeEnum.PARTNER_CODE_OK.code,
    msg=CodeEnum.PARTNER_CODE_OK.msg,
    data={"id": 1}
)
"""

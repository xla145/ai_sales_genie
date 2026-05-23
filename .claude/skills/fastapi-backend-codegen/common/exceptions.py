# -*- coding: utf-8 -*-
"""
异常处理模块
生成代码时可以直接导入使用: from app.exceptions.exceptions import BusinessException, IdNotExist
"""
import typing

from app.corelibs.codes import CodeEnum


class MyBaseException(Exception):
    """基础异常类"""
    def __init__(self, err_or_code: typing.Union[CodeEnum, str]):
        if isinstance(err_or_code, CodeEnum):
            code = err_or_code.code
            msg = err_or_code.msg
        else:
            code = CodeEnum.PARTNER_CODE_FAIL.code
            msg = err_or_code
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"{self.code}:{self.msg}"

    def __repr__(self):
        return f"{self.code}:{self.msg}"


class IpError(MyBaseException):
    """IP错误"""
    def __init__(self):
        super(IpError, self).__init__("ip 错误")


class SetRedis(MyBaseException):
    """Redis存储失败"""
    def __init__(self):
        super(SetRedis, self).__init__("Redis存储失败")


class IdNotExist(MyBaseException):
    """查询id不存在"""
    def __init__(self):
        super(IdNotExist, self).__init__("查询id不存在")


class UserNotExist(MyBaseException):
    """用户不存在"""
    def __init__(self):
        super(UserNotExist, self).__init__("用户不存在")


class AccessTokenFail(MyBaseException):
    """访问令牌失败"""
    def __init__(self):
        super(AccessTokenFail, self).__init__(CodeEnum.PARTNER_CODE_TOKEN_EXPIRED_FAIL)


class ErrorUser(MyBaseException):
    """错误的用户名或密码"""
    def __init__(self):
        super(ErrorUser, self).__init__("错误的用户名或密码")


class PermissionNotEnough(MyBaseException):
    """权限不足,拒绝访问"""
    def __init__(self):
        super(PermissionNotEnough, self).__init__("权限不足,拒绝访问")


class ParameterError(MyBaseException):
    """参数错误"""
    def __init__(self, err_code: typing.Union[CodeEnum, str]):
        super(ParameterError, self).__init__(err_code)


class SystemException(MyBaseException):
    """系统异常 - 统一处理未定义的异常"""
    def __init__(self, message: str = None, code: int = None):
        if message is None:
            message = "系统异常，请联系管理员"
        if code is None:
            code = CodeEnum.PARTNER_CODE_FAIL.code
        self.code = code
        self.msg = message
        super(SystemException, self).__init__(message)


class BusinessException(MyBaseException):
    """业务异常 - 业务逻辑相关异常"""
    def __init__(self, message: str, code: int = None):
        if code is None:
            code = CodeEnum.PARTNER_CODE_FAIL.code
        self.code = code
        self.msg = message
        super(BusinessException, self).__init__(message)


class DatabaseException(MyBaseException):
    """数据库异常"""
    def __init__(self, message: str = "数据库操作异常"):
        super(DatabaseException, self).__init__(message)


class ValidationException(MyBaseException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败"):
        super(ValidationException, self).__init__(message)


class AuthenticationException(MyBaseException):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        super(AuthenticationException, self).__init__(message)


class AuthorizationException(MyBaseException):
    """授权异常"""
    def __init__(self, message: str = "权限不足"):
        super(AuthorizationException, self).__init__(message)

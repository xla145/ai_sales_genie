# 公共模块总览

本目录包含所有可直接使用的公共模块代码和说明文档。这些模块在实际项目中已经存在，生成代码时直接导入使用即可。

## 模块列表

### 1. 核心模块

| 文件 | 实际位置 | 说明 | 主要导出 |
|------|---------|------|---------|
| `db.py` | `app/db/sqlalchemy.py` | 数据库连接和事务管理 | `async_session`, `async_transaction` |
| `redis.py` | `app/db/redis.py` | Redis连接和操作 | `redis_pool`, `MyAsyncRedis` |
| `config.py` | `app/config.py` | 应用配置管理 | `Settings`, `settings` |
| `deps.py` | `app/api/deps.py` | API依赖注入 | `get_db`, `get_redis` |


### 2. 异常和工具

| 文件 | 实际位置 | 说明 | 主要导出 |
|------|---------|------|---------|
| `exceptions.py` | `app/exceptions/exceptions.py` | 异常类定义 | `BusinessException`, `IdNotExist`等 |
| `corelibs.py` | `app/corelibs/` | 核心库说明文档 | - |
| `utils.py` | `app/utils/` | 工具函数说明文档 | - |

### 3. Schema和应用

| 文件 | 实际位置 | 说明 | 主要导出 |
|------|---------|------|---------|
| `schemas.py` | `app/schemas/common.py` | Schema基础类 | `BaseSchema`, `Response`, `PageResponse` |
| `main.py` | `backend/main.py` | 应用入口文件模板 | `create_app`, `app` |
| `base_model_usage.md` | `app/models/base.py` | Base模型使用指南 | - |

### 4. 初始化模块

| 文件 | 实际位置 | 说明 | 主要导出 |
|------|---------|------|---------|
| `init_modules.py` | `app/init/` | 初始化模块说明文档 | - |

### 5. 文档

| 文件 | 说明 |
|------|------|
| `usage_examples.md` | 详细使用示例 |
| `imports_reference.md` | 所有模块的导入方式参考 |

## 快速导入参考

### Model层常用导入

```python
from app.models.base import Base
from sqlalchemy import Column, String, Integer
```

### Service层常用导入

```python
from app.models.user import User as UserModel
from app.exceptions.exceptions import IdNotExist, BusinessException
from app.corelibs.logger import logger
from app.db.redis import redis_pool  # 如需使用缓存
```

### API层常用导入

```python
from app.corelibs.custom_router import APIRouter
from app.utils.response import HttpResponse
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
```

### 应用入口常用导入

```python
from app.init.routers import init_router
from app.init.exception import init_exception
from app.init.cors import init_cors
from app.db import redis_pool
from app.corelibs.logger import init_logger
from app.config import settings
```

## 使用说明

1. **这些模块已存在**：`common/` 目录下的模块在实际项目中已经存在，生成代码时直接导入使用即可，不需要复制代码。

2. **查看详细文档**：
   - 查看 `imports_reference.md` 了解所有模块的导入方式
   - 查看 `usage_examples.md` 了解详细使用示例
   - 查看各个模块文件了解具体功能

3. **代码生成时**：
   - 直接使用这些导入语句
   - 不需要重新实现这些功能
   - 遵循项目的架构规范

## 注意事项

- 所有模块都是标准的，可以直接使用
- Base模型的所有方法已经包含事务管理
- Redis连接需要在应用启动时初始化
- 异常会被全局异常处理器自动捕获
- 响应统一使用HttpResponse类

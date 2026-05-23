# 公共模块导入参考

本文档列出所有公共模块的导入方式和使用说明。

## 1. 数据库相关

### 数据库连接
```python
from app.db.sqlalchemy import async_session, async_transaction, content_transaction
```

### Base模型（所有Model必须继承）
```python
from app.models.base import Base

# Base模型提供了完整的CRUD方法：
# - get(id, to_dict=False): 根据ID查询
# - get_all(): 查询所有记录
# - create(params, to_dict=False): 创建记录
# - update(params): 更新记录
# - update_non_null_fields(params): 更新非空字段（推荐）
# - delete(id, _hard=False): 删除记录（默认软删除）
# - pagination(stmt): 分页查询
# - batch_create(params_list): 批量创建
# 等等...

# 使用示例：
class User(Base):
    __tablename__ = "users"
    name = Column(String(255))
    
    # 自动获得所有Base提供的方法
    # await User.get(id)
    # await User.create({"name": "test"})
```

**详细使用说明请查看**: `common/base_model_usage.md`

## 2. Redis相关

```python
from app.db.redis import redis_pool, MyAsyncRedis, RedisPool
```

## 3. 配置相关

```python
from app.config import settings
```

## 4. API相关

### 依赖注入
```python
from app.api.deps import get_db, get_redis
```

### 自定义路由
```python
from app.corelibs.custom_router import APIRouter
```

## 5. 异常处理

```python
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
```

## 6. 响应工具

```python
from app.utils.response import HttpResponse
```

## 7. 日志

```python
from app.corelibs.logger import logger, init_logger
```

## 8. 状态码

```python
from app.corelibs.codes import CodeEnum
```

## 9. Schema基础类

```python
from app.schemas.common import BaseSchema
```

## 10. 上下文管理

```python
from app.utils.context import AppTraceId, SQLAlchemySession, FastApiRequest
```

## 11. 工具函数

```python
from app.utils.common import get_str_uuid, md5_encrypt, is_empty_string
```

## 12. 应用初始化

```python
from app.init.routers import init_router
from app.init.exception import init_exception
from app.init.cors import init_cors
from app.init.middleware import init_middleware
```

## 14. API路由聚合

```python
from app.api.api_router import router

# 在init_router中使用
app.include_router(router, prefix=settings.API_V1_PREFIX)
```

## 13. 常量

```python
from app.corelibs.consts import DEFAULT_PAGE, DEFAULT_PER_PAGE, CACHE_HOUR, CACHE_DAY
```

## 完整导入示例

### Model层
```python
from app.models.base import Base
from sqlalchemy import Column, String
```

### Service层
```python
from app.models.user import User as UserModel
from app.exceptions.exceptions import IdNotExist, BusinessException
from app.corelibs.logger import logger
from app.db.redis import redis_pool  # 如需使用缓存
```

### API层
```python
from app.corelibs.custom_router import APIRouter
from app.utils.response import HttpResponse
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
```

### 应用入口
```python
from app.init.routers import init_router
from app.init.exception import init_exception
from app.init.cors import init_cors
from app.db import redis_pool
from app.corelibs.logger import init_logger
from app.config import settings
```

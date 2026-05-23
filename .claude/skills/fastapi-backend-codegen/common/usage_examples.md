# 公共模块使用示例

## 1. 数据库连接使用

### 导入数据库模块

```python
from app.db.sqlalchemy import async_session, async_transaction
from app.models.base import Base
```

### 在Model中使用（自动事务）

```python
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    # Base类的方法已经使用@async_transaction装饰器
    # 所以所有操作都自动在事务中执行
    @classmethod
    async def create_user(cls, name: str):
        # 这个方法会自动在事务中执行
        return await cls.create({"name": name})
```

### 手动使用事务

```python
from app.db.sqlalchemy import content_transaction

async def complex_operation():
    async with content_transaction() as session:
        # 执行多个数据库操作
        user = await User.create({"name": "test"})
        profile = await Profile.create({"user_id": user.id})
        # 如果任何操作失败，会自动回滚
```

### 使用async_transaction装饰器

```python
from app.db.sqlalchemy import async_transaction

@async_transaction
async def my_service_method():
    # 这个方法会自动在事务中执行
    user = await User.create({"name": "test"})
    return user
```

## 2. Redis使用

### 导入Redis模块

```python
from app.db.redis import redis_pool
```

### 初始化Redis（在应用启动时）

```python
from app.db.redis import redis_pool
from app.config import settings

# 在应用启动时初始化
redis_pool.init_by_config(settings)
```

### 使用Redis

```python
from app.db.redis import redis_pool

# 获取Redis客户端
redis = redis_pool.get_redis()

# 设置值（自动JSON序列化）
await redis.set("key", {"name": "test", "age": 20}, ex=3600)

# 获取值（自动JSON反序列化）
data = await redis.get("key")  # 返回: {"name": "test", "age": 20}

# 列表操作
await redis.cus_lpush("list_key", {"item": 1})
item = await redis.cus_lpop("list_key")

# Hash操作
await redis.hset("hash_key", "field", {"data": "value"})
```

### 缓存示例

```python
from app.db.redis import redis_pool

class CacheService:
    @staticmethod
    async def get_user_cache(user_id: int):
        redis = redis_pool.get_redis()
        cache_key = f"user:{user_id}"
        
        # 尝试从缓存获取
        cached = await redis.get(cache_key)
        if cached:
            return cached
        
        # 从数据库获取
        user = await User.get(user_id)
        
        # 写入缓存（7天过期）
        await redis.set(cache_key, user, ex=7*24*3600)
        
        return user
```

## 3. 配置使用

### 导入配置

```python
from app.config import settings
```

### 使用配置

```python
from app.config import settings

# 数据库URL
db_url = settings.DATABASE_URL

# Redis URI
redis_uri = settings.REDIS_URI

# 应用配置
debug = settings.DEBUG
api_prefix = settings.API_V1_PREFIX

# 文件上传配置
upload_dir = settings.UPLOAD_DIR
max_upload_size = settings.MAX_UPLOAD_SIZE

# CORS配置
cors_origins = settings.CORS_ORIGINS.split(",")
```

## 4. 完整示例：Service中使用数据库和Redis

```python
from app.models.user import User as UserModel
from app.db.redis import redis_pool
from app.corelibs.logger import logger
from app.exceptions.exceptions import IdNotExist, BusinessException

class UserService:
    @staticmethod
    async def get_user_with_cache(user_id: int):
        """获取用户（带缓存）"""
        redis = redis_pool.get_redis()
        cache_key = f"user:{user_id}"
        
        # 尝试从缓存获取
        cached = await redis.get(cache_key)
        if cached:
            logger.info(f"从缓存获取用户: {user_id}")
            return cached
        
        # 从数据库获取
        user = await UserModel.get(user_id)
        if not user:
            raise IdNotExist()
        
        # 写入缓存（1小时过期）
        await redis.set(cache_key, user, ex=3600)
        logger.info(f"从数据库获取用户并缓存: {user_id}")
        
        return user
    
    @staticmethod
    async def create_user(data: dict):
        """创建用户"""
        # 检查用户名是否已存在
        exist_user = await UserModel.get_by_username(data["username"])
        if exist_user:
            raise BusinessException("用户名已存在")
        
        # 创建用户（自动在事务中执行）
        user = await UserModel.create(data)
        
        # 清除相关缓存
        redis = redis_pool.get_redis()
        await redis.delete(f"user:{user.id}")
        
        return user
```

## 5. 注意事项

1. **数据库连接**：
   - Base模型的所有方法已经使用`@async_transaction`装饰器
   - 不需要手动管理事务
   - 多个Model操作会自动在同一事务中执行

2. **Redis连接**：
   - 需要在应用启动时初始化：`redis_pool.init_by_config(settings)`
   - 所有操作都是异步的，使用`await`
   - 值会自动进行JSON序列化/反序列化

3. **配置**：
   - 配置从`.env`文件或环境变量读取
   - 使用`settings.XXX`访问配置项
   - 修改配置后需要重启应用

# FastAPI Backend Code Generation Skill

这是一个用于生成FastAPI后端代码的Skill，遵循严格的Model-Service-API分层架构模式。

## 技术栈

### 核心框架与库

- **Web框架**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0.23+
- **数据验证**: Pydantic 2.5.0+
- **配置管理**: Pydantic Settings 2.1.0+
- **Python版本**: 3.10+ (需要async/await支持)

### 数据库与缓存

- **数据库**: MySQL 8.0+ (通过 aiomysql 0.2.0+)
- **缓存/队列**: Redis 5.0+ (通过 redis 5.0.1+)
- **数据库迁移**: Alembic 1.12.1+

### 核心依赖

```python
# 核心框架
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0

# 数据库
aiomysql==0.2.0
cryptography==41.0.7
alembic==1.12.1

# Redis
redis==5.0.1
hiredis==2.2.3

# 工具库
loguru==0.7.2
python-dotenv==1.0.0
orjson==3.8.6
```

### 可选依赖

- **异步任务**: Celery 5.3.4+ (用于后台任务)
- **Excel处理**: pandas 2.1.3+, openpyxl 3.1.2+
- **身份认证**: python-jose[cryptography] 3.3.0+, passlib[bcrypt] 1.7.4+

### 架构特性

- **异步/等待**: 所有数据库操作使用async/await
- **分层架构**: API → Service → Model → Database
- **依赖注入**: 使用FastAPI Depends进行数据库会话和Redis连接管理
- **事务管理**: 通过装饰器自动包装事务

## 目录结构

```
fastapi-backend-codegen/
├── SKILL.md                    # Skill主文档（包含使用说明）
├── README.md                   # 本文件
├── templates/                  # 代码模板
│   ├── model_template.py       # Model层模板
│   ├── service_template.py     # Service层模板
│   ├── schema_template.py     # Schema层模板
│   └── api_template.py        # API层模板
├── common/                     # 公共模块（可直接使用）
│   ├── __init__.py            # 模块说明
│   ├── db.py                  # 数据库连接模块
│   ├── redis.py               # Redis连接模块
│   ├── config.py              # 配置模块
│   ├── deps.py                # API依赖注入
│   ├── exceptions.py          # 异常类定义
│   ├── corelibs.py            # 核心库说明
│   ├── init_modules.py        # 初始化模块说明
│   ├── utils.py               # 工具函数说明
│   ├── schemas.py             # Schema基础类
│   ├── main.py                # 应用入口文件模板
│   ├── base_model_usage.md    # Base模型使用指南
│   ├── usage_examples.md      # 使用示例
│   └── imports_reference.md   # 导入参考文档
├── utils/                      # 工具参考文档
│   ├── base_model_reference.py    # Base模型参考
│   ├── response_reference.py      # 响应工具参考
│   └── exception_reference.py     # 异常处理参考
└── examples/                   # 示例代码
    └── complete_crud_example.md   # 完整CRUD示例
```

## 如何使用这个Skill

### 方式一：在AI助手中使用（推荐）

当你在AI助手中需要生成FastAPI后端代码时，可以这样使用：

#### 1. 引用Skill文档

在对话中引用Skill文档：
```
@SKILL.md 请帮我生成一个User模块的完整CRUD代码
```

或者：
```
使用 @fastapi-backend-codegen 技能，生成Product模块的Model、Service、Schema和API代码
```

#### 2. 指定生成内容

你可以要求生成：
- **完整模块**：`生成User模块的完整CRUD代码（包括Model、Service、Schema、API）`
- **单个层**：`生成User模块的Model层代码`
- **特定功能**：`生成User模块的分页查询功能`

#### 3. 提供业务信息

提供必要的业务信息，AI会根据Skill规范生成代码：
```
生成Order模块，包含以下字段：
- order_no: 订单号（字符串，唯一）
- user_id: 用户ID（整数）
- total_amount: 总金额（小数）
- status: 状态（字符串：pending, paid, shipped, completed）
- order_date: 订单日期（日期时间）
```

#### 4. 代码生成示例

**示例1：生成完整CRUD模块**
```
@SKILL.md 请生成一个Article（文章）模块的完整代码，包含：
- 标题（title）
- 内容（content）
- 作者ID（author_id）
- 分类ID（category_id）
- 状态（status：draft, published, archived）
- 发布时间（publish_time）
```

**示例2：生成特定功能**
```
@SKILL.md 为Project模块添加一个根据状态和创建时间范围查询的方法
```

**示例3：生成复杂查询**
```
@SKILL.md 为User模块添加一个统计方法，返回每个角色的用户数量
```

### 方式二：手动使用模板

#### 1. 查看Skill文档

阅读 `SKILL.md` 了解架构原则和使用方法。

#### 2. 使用模板

复制 `templates/` 目录下的模板文件，替换占位符：
- `{ModelName}` → 模型名称（如 User）
- `{model_name}` → 模型名称小写（如 user）
- `{table_name}` → 表名（如 users）
- `{api_prefix}` → API前缀（如 users）
- `{model_file}` → 模型文件名（如 user）
- `{schema_file}` → Schema文件名（如 user）
- `{service_file}` → Service文件名（如 user_service）

#### 3. 使用公共模块

`common/` 目录包含所有可直接使用的公共模块：

**核心模块：**
- `db.py` - 数据库连接（async_session, async_transaction）
- `redis.py` - Redis连接（redis_pool）
- `config.py` - 配置管理（settings）
- `deps.py` - API依赖注入（get_db, get_redis）

**异常和工具：**
- `exceptions.py` - 异常类定义（BusinessException, IdNotExist等）
- `corelibs.py` - 核心库说明（custom_router, logger, codes等）
- `utils.py` - 工具函数说明（response, context, serialize等）

**Schema和应用：**
- `schemas.py` - Schema基础类（BaseSchema）
- `main.py` - 应用入口文件模板
- `base_model_usage.md` - Base模型使用指南（包含所有CRUD方法说明）

**初始化模块：**
- `init_modules.py` - 初始化模块说明（routers, exception, cors等）

查看 `common/usage_examples.md` 和 `common/imports_reference.md` 了解详细使用方法。

#### 4. 参考示例

查看 `examples/complete_crud_example.md` 了解完整实现。

#### 5. 查看Base模型使用指南

查看 `common/base_model_usage.md` 了解Base模型的所有CRUD方法和使用示例。

#### 6. 查看工具参考

查看 `utils/` 目录下的参考文档了解公共类的使用方法。

## 使用注意事项

### 1. 遵循架构原则

- ✅ **正确**：Service层调用Model层方法
  ```python
  # Service层
  user = await UserModel.get(user_id)
  ```

- ❌ **错误**：Service层直接操作数据库
  ```python
  # Service层 - 错误示例
  result = await db.execute(select(User).where(User.id == user_id))
  ```

### 2. 使用Base模型

- ✅ **正确**：所有Model继承Base类
  ```python
  from app.models.base import Base
  class User(Base):
      __tablename__ = "users"
  ```

- ❌ **错误**：直接继承SQLAlchemy的declarative_base
  ```python
  # 错误示例
  from sqlalchemy.ext.declarative import declarative_base
  Base = declarative_base()
  ```

### 3. 公共字段自动管理

Base模型会自动管理以下字段，无需手动设置：
- `creation_date` - 创建时间（自动设置）
- `created_by` - 创建人ID（从请求token自动提取）
- `updation_date` - 更新时间（自动更新）
- `updated_by` - 更新人ID（从请求token自动提取）
- `enabled_flag` - 删除标志（默认1，查询时自动过滤）
- `trace_id` - 追踪ID（从上下文自动提取）

### 4. 查询时自动过滤删除记录

所有Base模型的查询方法会自动过滤 `enabled_flag=0` 的记录，无需手动添加条件。

### 5. 使用统一的响应格式

API层应使用 `HttpResponse` 返回统一格式的响应：
```python
from app.utils.response import HttpResponse

return await HttpResponse.success(data=result, msg="操作成功")
```

### 6. 异常处理

使用自定义异常类，不要直接抛出通用异常：
```python
from app.exceptions.exceptions import BusinessException, IdNotExist

if not user:
    raise IdNotExist()
if user.status != "active":
    raise BusinessException("用户状态不正确")
```

## 使用场景示例

### 场景1：生成新模块的完整CRUD

**请求：**
```
@SKILL.md 生成一个Comment（评论）模块的完整代码，包含：
- 文章ID（article_id）
- 用户ID（user_id）
- 内容（content）
- 父评论ID（parent_id，可选，用于回复）
- 状态（status：pending, approved, rejected）
```

**AI会生成：**
- `app/models/comment.py` - Model层（继承Base，包含CRUD方法）
- `app/services/comment_service.py` - Service层（业务逻辑）
- `app/schemas/comment.py` - Schema层（数据验证）
- `app/api/v1/comments.py` - API层（路由定义）

### 场景2：为现有模块添加新功能

**请求：**
```
@SKILL.md 为Project模块添加一个批量更新状态的功能
```

**AI会生成：**
- Service层方法：`batch_update_status()`
- API层路由：`PUT /projects/batch-update-status`

### 场景3：生成复杂查询功能

**请求：**
```
@SKILL.md 为Order模块添加一个统计功能，返回：
- 按状态分组的订单数量
- 按日期分组的订单金额
- 最近7天的订单趋势
```

**AI会生成：**
- Model层方法：`get_statistics_by_status()`, `get_statistics_by_date()`
- Service层方法：`get_order_statistics()`
- API层路由：`GET /orders/statistics`

### 场景4：生成关联查询

**请求：**
```
@SKILL.md 为User模块添加一个获取用户及其所有订单的方法
```

**AI会生成：**
- Model层方法：`get_user_with_orders()`
- Service层方法：`get_user_detail()`
- Schema层：`UserDetail`（包含订单列表）
- API层路由：`GET /users/{id}/detail`

## 核心原则

1. **所有数据库操作必须经过Model层**
2. **职责划分明确**：Model层不包含业务逻辑，Service层不直接操作数据库
3. **公共字段自动管理**：creation_date, created_by等字段自动填充

## 代码生成检查清单

生成代码后，请检查：

- [ ] Model层继承自Base类
- [ ] 查询方法包含enabled_flag == 1条件
- [ ] Service层只调用Model层方法
- [ ] API层使用HttpResponse返回响应
- [ ] Schema层继承自BaseSchema

## 更多信息

- 查看 `SKILL.md` 获取详细使用说明
- 查看 `examples/` 获取代码示例
- 查看 `utils/` 获取工具类参考

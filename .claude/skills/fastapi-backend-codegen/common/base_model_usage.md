# Base模型使用指南

Base模型是所有Model的基础类，提供了完整的CRUD操作和公共字段管理。

## 导入方式

```python
from app.models.base import Base
```

## 公共字段

所有继承Base的模型自动获得以下字段：

- `id`: BIGINT, 主键, 自增
- `creation_date`: DATETIME, 创建时间, 自动设置
- `created_by`: BIGINT, 创建人ID, 自动从token获取
- `updation_date`: DATETIME, 更新时间, 自动更新
- `updated_by`: BIGINT, 更新人ID, 自动从token获取
- `enabled_flag`: BOOLEAN, 是否删除(0删除,1未删除), 默认1
- `trace_id`: VARCHAR(255), 追踪ID, 自动从上下文获取

## CRUD操作方法

### 1. 查询方法

#### get() - 根据ID查询单条记录

```python
# 返回模型对象
result = await Model.get(id)

# 返回字典
result = await Model.get(id, to_dict=True)
```

**特点**：
- 自动过滤 `enabled_flag=1` 的记录
- 如果记录不存在或已删除，返回 `None`

#### get_all() - 查询所有记录

```python
results = await Model.get_all()  # 返回 list[dict]
```

**特点**：
- 自动过滤已删除记录
- 按ID倒序排列
- 返回字典列表

#### pagination() - 分页查询

```python
stmt = select(*Model.get_table_columns()).where(Model.enabled_flag == 1)
results = await Model.pagination(stmt)
```

**返回格式**：
```python
{
    "rowTotal": 100,      # 总记录数
    "pageSize": 10,       # 每页数量
    "page": 1,            # 当前页码
    "pageTotal": 10,      # 总页数
    "rows": [...]         # 数据列表
}
```

**特点**：
- 自动从请求参数中获取 `page` 和 `pageSize`
- 支持GET和POST请求
- 默认每页10条，最大1000条

### 2. 创建方法

#### create() - 创建单条记录

```python
params = {"name": "test", "description": "desc"}
result = await Model.create(params)  # 返回模型对象
result = await Model.create(params, to_dict=True)  # 返回字典
```

**特点**：
- 自动填充 `creation_date`, `created_by`, `trace_id`
- 自动在事务中执行
- 返回创建后的记录

#### batch_create() - 批量创建

```python
params_list = [
    {"name": "test1"},
    {"name": "test2"}
]
count = await Model.batch_create(params_list)  # 返回插入数量
```

**特点**：
- 批量插入，性能更好
- 自动填充公共字段
- 返回插入的记录数

### 3. 更新方法

#### update() - 全量更新

```python
params = {"id": 1, "name": "new_name", "description": None}
result = await Model.update(params)
```

**特点**：
- 更新所有字段，包括None值
- 自动填充 `updation_date`, `updated_by`
- 自动在事务中执行

#### update_non_null_fields() - 更新非空字段（推荐）

```python
params = {"id": 1, "name": "new_name"}  # description不会被更新
result = await Model.update_non_null_fields(params)
```

**特点**：
- 只更新提供的非None字段
- 忽略未提供的字段
- 推荐使用此方法

#### update_with_conditions() - 根据条件更新

```python
where_conditions = [Model.status == "active"]
params = {"status": "inactive"}
await Model.update_with_conditions(params, where_conditions)
```

**特点**：
- 支持复杂的更新条件
- 可以批量更新多条记录

### 4. 删除方法

#### delete() - 软删除（默认）

```python
count = await Model.delete(id)  # 设置enabled_flag=0
```

**特点**：
- 默认软删除（设置 `enabled_flag=0`）
- 数据不会真正删除
- 查询时自动过滤

#### delete() - 物理删除

```python
count = await Model.delete(id, _hard=True)  # 真正删除记录
```

**特点**：
- 真正从数据库删除
- 谨慎使用

#### delete_with_conditions() - 根据条件删除

```python
where_conditions = [Model.status == "deleted"]
count = await Model.delete_with_conditions(where_conditions)
```

## 自定义查询方法

在Model类中定义业务相关的查询方法：

```python
class User(Base):
    __tablename__ = "users"
    
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="active")
    
    @classmethod
    async def get_by_status(cls, status: str):
        """按状态查询用户列表"""
        query_conditions = [
            cls.enabled_flag == 1,  # 必须包含此条件
            cls.status == status
        ]
        stmt = select(*cls.get_table_columns()).where(and_(*query_conditions))
        return await cls.get_result(stmt)
    
    @classmethod
    async def get_data_with_pagination(cls, status: str = None, name: str = None):
        """分页查询用户"""
        query_conditions = [cls.enabled_flag == 1]  # 必须包含此条件
        if status:
            query_conditions.append(cls.status == status)
        if name:
            query_conditions.append(cls.name.like(f"%{name}%"))
        stmt = select(*cls.get_table_columns()).where(and_(*query_conditions))
        return await cls.pagination(stmt)
```

## 重要注意事项

1. **所有查询必须包含 `enabled_flag == 1` 条件**
   ```python
   query_conditions = [cls.enabled_flag == 1]
   ```

2. **使用 `get_table_columns()` 返回字典**
   ```python
   stmt = select(*cls.get_table_columns()).where(...)
   ```

3. **Base方法已包含事务管理**
   - 所有方法都使用 `@async_transaction` 装饰器
   - 不需要手动管理事务

4. **公共字段自动填充**
   - `created_by`, `updated_by` 自动从请求token获取
   - `trace_id` 自动从上下文获取
   - 无需手动设置

5. **查询自动过滤已删除记录**
   - `get()`, `get_all()` 等方法自动过滤 `enabled_flag=1`
   - 自定义查询方法需要手动添加此条件

## 完整示例

```python
from app.models.base import Base
from sqlalchemy import Column, String, Integer, Index
from sqlalchemy import select, and_

class User(Base):
    __tablename__ = "users"
    
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    status = Column(String(50), default="active")
    
    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_status", "status"),
    )
    
    @classmethod
    async def get_by_username(cls, username: str):
        """根据用户名查询"""
        query_conditions = [
            cls.enabled_flag == 1,
            cls.username == username
        ]
        stmt = select(cls).where(and_(*query_conditions))
        return (await cls.execute(stmt)).scalar_one_or_none()
    
    @classmethod
    async def get_data_with_pagination(cls, status: str = None, username: str = None):
        """分页查询"""
        query_conditions = [cls.enabled_flag == 1]
        if status:
            query_conditions.append(cls.status == status)
        if username:
            query_conditions.append(cls.username.like(f"%{username}%"))
        stmt = select(*cls.get_table_columns()).where(and_(*query_conditions))
        return await cls.pagination(stmt)
```

## 方法列表

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `get(id, to_dict=False)` | 根据ID查询 | 模型对象或字典 |
| `get_all()` | 查询所有记录 | list[dict] |
| `create(params, to_dict=False)` | 创建记录 | 模型对象或字典 |
| `batch_create(params_list)` | 批量创建 | int (插入数量) |
| `update(params, to_dict=False)` | 全量更新 | 模型对象或字典 |
| `update_non_null_fields(params)` | 更新非空字段 | 模型对象或字典 |
| `update_with_conditions(params, where_conditions)` | 条件更新 | 模型对象或字典 |
| `delete(id, _hard=False)` | 删除记录 | int (影响行数) |
| `delete_with_conditions(where_conditions, _hard=False)` | 条件删除 | int (影响行数) |
| `pagination(stmt)` | 分页查询 | dict (分页结果) |
| `get_result(stmt, first=False)` | 执行查询 | list[dict] 或 dict |
| `get_table_columns(exclude=None)` | 获取表字段 | ClauseList |
| `create_or_update(params)` | 创建或更新 | dict |

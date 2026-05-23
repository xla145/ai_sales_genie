# CRUD Module Generation Reference

## Module Structure

| Layer | File Location | Purpose |
|-------|---------------|---------|
| **Model** | `app/models/[entity].py` | Table definition, database operations |
| **Schema** | `app/schemas/[entity].py` | Request/Response validation |
| **Service** | `app/services/[entity]_service.py` | Business logic |
| **API** | `app/api/v1/[entities].py` | HTTP endpoints |

---

## Model Layer Pattern

### Required Components

| Component | Required | Purpose |
|-----------|----------|---------|
| **Inheritance** | ✅ | Must inherit from `Base` |
| **Table Name** | ✅ | `__tablename__` attribute |
| **Business Fields** | ✅ | SQLAlchemy Column definitions |
| **Indexes** | ⚠️ | Add for frequently queried fields |
| **Custom Queries** | ⚠️ | Encapsulate complex queries |

### Field Definition Pattern

```python
from sqlalchemy import Column, String, Text, Index
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    # Business fields
    username = Column(String(100), nullable=False, comment="用户名")
    email = Column(String(255), nullable=False, comment="邮箱")
    full_name = Column(String(255), comment="全名")
    status = Column(String(50), default="active", nullable=False, comment="状态")

    # Indexes and table comment
    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_email", "email"),
        {"comment": "用户表"}
    )
```

### Custom Query Methods Pattern

**Single record query:**
```python
@classmethod
async def get_by_username(cls, username: str):
    """根据用户名查询"""
    query_conditions = [
        cls.enabled_flag == 1,
        cls.username == username
    ]
    stmt = select(cls).where(and_(*query_conditions))
    return (await cls.execute(stmt)).scalar_one_or_none()
```

**Paginated query:**
```python
@classmethod
async def get_data_with_pagination(cls, status: str = None, username: str = None):
    """分页查询"""
    query_conditions = [cls.enabled_flag == 1]
    if status:
        query_conditions.append(cls.status == status)
    if username:
        query_conditions.append(cls.username.like(f"%{username}%"))

    stmt = select(*cls.get_table_columns()).where(
        and_(*query_conditions)
    ).order_by(cls.creation_date.desc())

    return await cls.pagination(stmt)
```

**Important:**
- [ ] Always include `enabled_flag == 1` in conditions
- [ ] Use `get_table_columns()` for pagination queries
- [ ] Use `and_(*query_conditions)` for multiple conditions
- [ ] Order by relevant field (usually creation_date)

---

## Schema Layer Pattern

### Four Schema Pattern

```python
from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema

# 1. Base Schema - Shared fields
class UserBase(BaseSchema):
    username: str
    email: str
    full_name: Optional[str] = None
    status: Optional[str] = "active"

# 2. Create Schema - Required fields for creation
class UserCreate(UserBase):
    password: str  # Additional required field

# 3. Update Schema - All fields optional
class UserUpdate(BaseSchema):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    status: Optional[str] = None

# 4. Response Schema - Includes ID and timestamps
class User(UserBase):
    id: int
    creation_date: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    updation_date: datetime
```

**Schema Responsibilities:**

| Schema | Inherits From | Optional Fields | Purpose |
|--------|---------------|-----------------|---------|
| Base | `BaseSchema` | Some | Shared field definitions |
| Create | Base | Few | Creation validation |
| Update | `BaseSchema` | All | Update validation |
| Response | Base | Some | API response |

---

## Service Layer Pattern

### Standard CRUD Operations

```python
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate
from app.exceptions.exceptions import IdNotExist, BusinessException

class UserService:
    """用户服务类"""

    @staticmethod
    async def create_user(data: UserCreate):
        """创建"""
        # Business validation
        exist_user = await UserModel.get_by_username(data.username)
        if exist_user:
            raise BusinessException("用户名已存在")

        # Data preparation
        create_data = data.model_dump()
        # ... additional processing

        # Call Model layer
        return await UserModel.create(create_data)

    @staticmethod
    async def get_user(user_id: int):
        """获取详情"""
        result = await UserModel.get(user_id)
        if not result:
            raise IdNotExist()
        return result

    @staticmethod
    async def page_users(status: str = None, username: str = None):
        """分页查询"""
        return await UserModel.get_data_with_pagination(
            status=status,
            username=username
        )

    @staticmethod
    async def update_user(user_id: int, data: UserUpdate):
        """更新"""
        update_params = data.model_dump()
        return await UserModel.update(user_id, update_params)

    @staticmethod
    async def delete_user(user_id: int):
        """删除"""
        count = await UserModel.delete(user_id)
        if count == 0:
            raise IdNotExist()
        return count
```

### Service Method Checklist

- [ ] Use `@staticmethod` decorator
- [ ] Accept Pydantic schema as parameter
- [ ] Implement business validation
- [ ] Call Model layer methods only
- [ ] Raise `IdNotExist` when record not found
- [ ] Raise `BusinessException` for business errors
- [ ] Use `model_dump()` to convert schema to dict

---

## API Layer Pattern

### Router Setup

```python
from app.corelibs.custom_router import APIRouter
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.utils.response import HttpResponse

router = APIRouter()
```

### Standard Endpoints

**Create (POST):**
```python
@router.post("/users", response_model=User, status_code=201)
async def create_user(data: UserCreate):
    """创建用户"""
    db_user = await UserService.create_user(data)
    return await HttpResponse.success(data=db_user)
```

**List (GET):**
```python
@router.get("/users")
async def get_users(
    status: Optional[str] = None,
    username: Optional[str] = None,
):
    """获取用户列表"""
    data = await UserService.page_users(status=status, username=username)
    return await HttpResponse.success(data=data)
```

**Get by ID (GET):**
```python
@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """获取用户详情"""
    user = await UserService.get_user(user_id)
    return await HttpResponse.success(data=user)
```

**Update (PUT):**
```python
@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, data: UserUpdate):
    """更新用户"""
    user = await UserService.update_user(user_id, data)
    return await HttpResponse.success(data=user)
```

**Delete (DELETE):**
```python
@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """删除用户"""
    await UserService.delete_user(user_id)
    return await HttpResponse.success()
```

### API Endpoint Checklist

- [ ] Use `APIRouter` from `app.corelibs.custom_router`
- [ ] Set appropriate HTTP method and path
- [ ] Add `response_model` for typed responses
- [ ] Set `status_code=201` for create
- [ ] Set `status_code=204` for delete
- [ ] Use query parameters for list filters
- [ ] Use path parameters for ID
- [ ] Return `HttpResponse.success()`
- [ ] Let global exception handler catch errors

---

## Router Registration

In `app/api/api_router.py`:

```python
from app.api.v1 import users

# Include router with tags
router.include_router(users.router, tags=["用户"])
```

---

## Generation Checklist

### Before Code Generation

- [ ] Identify entity name (singular for Model/Service, plural for API)
- [ ] List all business fields with types
- [ ] Determine which fields need indexes
- [ ] Identify custom query requirements
- [ ] Check for business validation rules

### After Code Generation

**Model:**
- [ ] Inherits from Base
- [ ] Has __tablename__
- [ ] All fields defined with proper types
- [ ] Indexes added in __table_args__
- [ ] Custom queries include enabled_flag == 1

**Schema:**
- [ ] Four schemas defined (Base, Create, Update, Response)
- [ ] Create schema has required fields
- [ ] Update schema has all optional fields
- [ ] Response schema includes common fields

**Service:**
- [ ] All methods are static
- [ ] Business validation implemented
- [ ] Only calls Model layer
- [ ] Proper exception handling

**API:**
- [ ] All CRUD endpoints defined
- [ ] Correct HTTP methods and status codes
- [ ] Response models specified
- [ ] HttpResponse.success() used

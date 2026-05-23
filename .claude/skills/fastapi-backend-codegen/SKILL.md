---
name: fastapi-backend-codegen
description: Generate FastAPI backend code following the Model-Service-API architecture pattern with automatic field management, standardized responses, and best practices
version: 1.0.0
author: AI Quote Team
---

# FastAPI Backend Code Generation Skill

This skill helps generate FastAPI backend code following a strict layered architecture pattern where all database operations must go through the Model layer, with automatic management of common fields (creation_date, created_by, updation_date, updated_by, enabled_flag, trace_id).

## Technology Stack

### Core Framework & Libraries

- **Web Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0.23+
- **Data Validation**: Pydantic 2.5.0+
- **Configuration**: Pydantic Settings 2.1.0+
- **Python Version**: 3.10+ (requires async/await support)

### Database & Cache

- **Database**: PostgreSQL 14+ (via asyncpg, SQLAlchemy async driver `postgresql+asyncpg`)
- **Cache/Queue**: Redis 5.0+ (via redis 5.0.1+)
- **Database Migration**: Alembic 1.12.1+

### Key Dependencies

```python
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
asyncpg==0.29.0
cryptography==41.0.7
alembic==1.12.1

# Redis
redis==5.0.1
hiredis==2.2.3

# Utilities
loguru==0.7.2
python-dotenv==1.0.0
orjson==3.8.6
```

### Optional Dependencies

- **Async Tasks**: Celery 5.3.4+ (for background tasks)
- **Excel Processing**: pandas 2.1.3+, openpyxl 3.1.2+
- **Authentication**: python-jose[cryptography] 3.3.0+, passlib[bcrypt] 1.7.4+

### Architecture Pattern

- **Async/Await**: All database operations use async/await
- **Layered Architecture**: API → Service → Model → Database
- **Dependency Injection**: FastAPI Depends for database sessions and Redis connections
- **Transaction Management**: Automatic transaction wrapping via decorators

## Architecture Principles

### Layered Architecture

```
API Layer (api/v1/*.py)
    ↓ calls
Service Layer (services/*.py)
    ↓ calls
Model Layer (models/*.py)
    ↓ executes
Database
```

### Core Rules (MANDATORY - MUST ENFORCE)

**CRITICAL: Service Layer Database Operation Prohibition**

The Service layer is **ABSOLUTELY FORBIDDEN** from performing any direct database operations. This is a hard architectural constraint that must be enforced in all generated code.

**1. Service Layer - FORBIDDEN Operations:**
   - ❌ **NEVER** use `SQLAlchemySession.get()`
   - ❌ **NEVER** use `session.execute()`
   - ❌ **NEVER** import or use `select()` from SQLAlchemy
   - ❌ **NEVER** import or use `and_()`, `or_()` from SQLAlchemy
   - ❌ **NEVER** import or use `func` from SQLAlchemy
   - ❌ **NEVER** construct SQL queries
   - ❌ **NEVER** access database directly
   - ❌ **NEVER** use `@async_transaction` decorator (only Model layer uses this)

**2. Service Layer - REQUIRED Operations:**
   - ✅ **MUST** only call Model layer methods
   - ✅ **MUST** implement business logic
   - ✅ **MUST** validate business rules
   - ✅ **MUST** coordinate multiple Models
   - ✅ **MUST** handle exceptions

**3. Model Layer - REQUIRED Operations:**
   - ✅ **MUST** provide all database query methods
   - ✅ **MUST** encapsulate all SQL operations
   - ✅ **MUST** use `@async_transaction` decorator for custom queries
   - ✅ **MUST** include `enabled_flag == 1` in all queries
   - ✅ **MUST** provide methods like: `get_by_xxx()`, `page_xxx()`, `get_xxx_stats()`

**4. Code Examples:**

**✅ CORRECT - Service calls Model:**
```python
# Service Layer - CORRECT
class UserService:
    @staticmethod
    async def create_user(user_data: dict):
        # Call Model layer to check existence
        existing = await User.get_by_email(user_data["email"])
        if existing:
            raise BusinessException("User exists")

        # Call Model layer to create
        user = await User.create(user_data, to_dict=True)
        return user
```

**❌ WRONG - Service operates database:**
```python
# Service Layer - WRONG! NEVER DO THIS!
class UserService:
    @staticmethod
    @async_transaction  # ❌ WRONG! Only Model layer uses this
    async def create_user(user_data: dict):
        session = SQLAlchemySession.get()  # ❌ FORBIDDEN!
        stmt = select(User).where(...)      # ❌ FORBIDDEN!
        result = await session.execute(stmt) # ❌ FORBIDDEN!
```

**✅ CORRECT - Model provides query methods:**
```python
# Model Layer - CORRECT
class User(BaseModel):
    __tablename__ = "users"
    email = Column(String(255), unique=True)

    @classmethod
    async def get_by_email(cls, email: str):
        """Get user by email - encapsulates database operation"""
        from sqlalchemy import select, and_
        from common.utils.context import SQLAlchemySession
        from common.db.sqlalchemy import async_transaction

        @async_transaction
        async def _query():
            session = SQLAlchemySession.get()
            stmt = select(cls).where(
                and_(cls.email == email, cls.enabled_flag == True)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        return await _query()
```

**5. Responsibility Division:**
   - **Model Layer**: Define table structure, provide ALL database operations, encapsulate queries, NO business logic
   - **Service Layer**: Implement business logic, call Model layer ONLY, coordinate Models, validate business rules
   - **API Layer**: Handle HTTP requests, parameter validation, call Service layer ONLY

**6. Automatic Common Field Management:**
   - All tables inherit from `BaseModel`
   - Common fields auto-filled: `creation_date`, `created_by`, `updation_date`, `updated_by`, `trace_id`
   - Queries automatically filter deleted records (`enabled_flag=1`)

**7. Code Generation Checklist:**

Before generating Service layer code, verify:
- [ ] No `SQLAlchemySession.get()` in Service
- [ ] No `session.execute()` in Service
- [ ] No SQLAlchemy imports (`select`, `and_`, `func`) in Service
- [ ] No `@async_transaction` decorator in Service
- [ ] All database operations delegated to Model layer
- [ ] Model layer provides all necessary query methods

**8. Common Violations and Fixes:**

| Violation in Service Layer | Correct Fix |
|----------------------------|-------------|
| `session = SQLAlchemySession.get()` | Remove - call Model method instead |
| `stmt = select(Model).where(...)` | Create `Model.get_by_xxx()` method |
| `await session.execute(stmt)` | Call Model layer method |
| `func.count()` | Create `Model.get_count()` method |
| `@async_transaction` | Remove - only Model layer uses this |
| Complex query | Encapsulate in Model layer method |

## Base Model

All models MUST inherit from `Base` class (`app/models/base.py`). The Base model provides:

### Common Fields

All models automatically get these fields:

- `id`: BIGINT, primary key, auto-increment
- `creation_date`: DATETIME, auto-set on creation
- `created_by`: BIGINT, auto-filled from request token
- `updation_date`: DATETIME, auto-updated on modification
- `updated_by`: BIGINT, auto-filled from request token
- `enabled_flag`: BOOLEAN (0=deleted, 1=active), default=1, used for soft delete
- `trace_id`: VARCHAR(255), auto-filled from context

### Base Model CRUD Methods

The Base model provides complete CRUD operations:

**Query Methods:**
- `get(id, to_dict=False)` - Get single record by ID
- `get_all()` - Get all records (returns list[dict])
- `pagination(stmt)` - Paginated query (auto-reads page/pageSize from request)

**Create Methods:**
- `create(params, to_dict=False)` - Create single record
- `batch_create(params_list)` - Batch create records

**Update Methods:**
- `update(params, to_dict=False)` - Full update (includes None values)
- `update_non_null_fields(params, to_dict=False)` - Update non-null fields only (recommended)
- `update_with_conditions(params, where_conditions)` - Update by conditions

**Delete Methods:**
- `delete(id, _hard=False)` - Soft delete by default (sets enabled_flag=0)
- `delete_with_conditions(where_conditions, _hard=False)` - Delete by conditions

**Important Notes:**
- All Base methods are wrapped with `@async_transaction` decorator
- All queries automatically filter `enabled_flag=1`
- Common fields (`created_by`, `updated_by`, `trace_id`) are auto-filled
- Use `get_table_columns()` to return dictionaries instead of model objects

See `common/base_model_usage.md` for detailed usage examples.

## Code Generation Templates

### Model Layer Template

Location: `templates/model_template.py`

Key points:
- **MUST inherit from `Base` class** (`from app.models.base import Base`)
- Define business fields using SQLAlchemy `Column`
- Add indexes for frequently queried fields
- Create custom query methods for business needs
- **All queries MUST include `enabled_flag == 1` condition**
- Use `get_table_columns()` to return dictionaries instead of model objects
- Base model provides all CRUD methods automatically (get, create, update, delete, etc.)

**Example:**
```python
from app.models.base import Base
from sqlalchemy import Column, String, Index

class User(Base):
    __tablename__ = "users"
    name = Column(String(255), nullable=False)
    
    # Base provides: get(), create(), update(), delete(), pagination(), etc.
    # No need to implement these methods
```

### Service Layer Template

Location: `templates/service_template.py`

**CRITICAL RULES - Service Layer:**

**FORBIDDEN (Never do these):**
- ❌ Import `SQLAlchemySession` from `common.utils.context`
- ❌ Import `async_transaction` from `common.db.sqlalchemy`
- ❌ Import `select`, `and_`, `or_`, `func` from `sqlalchemy`
- ❌ Use `session.execute()`, `session.query()`, `session.add()`
- ❌ Construct SQL queries or statements
- ❌ Access database directly

**REQUIRED (Must do these):**
- ✅ Use static methods
- ✅ Call Model layer methods ONLY
- ✅ Implement business logic and validation
- ✅ Handle exceptions appropriately
- ✅ Use `BusinessException`, `IdNotExist` for errors
- ✅ Coordinate multiple Model calls if needed

**Example - Correct Service Layer:**
```python
from models.user import User
from models.role import Role
from common.exceptions.exceptions import BusinessException

class UserService:
    @staticmethod
    async def create_user(user_data: dict):
        # 1. Business validation
        if not user_data.get("email"):
            raise BusinessException("Email is required")

        # 2. Check existence - call Model layer
        existing = await User.get_by_email(user_data["email"])
        if existing:
            raise BusinessException("User already exists")

        # 3. Create user - call Model layer
        user = await User.create(user_data, to_dict=False)

        # 4. Assign default role - call Model layer
        default_role = await Role.get_by_name("user")
        if default_role:
            await User.assign_role(user.id, default_role.id)

        # 5. Return result - call Model layer
        return await User.get(user.id, to_dict=True)

    @staticmethod
    async def get_user_list(name: str = None, page: int = 1, page_size: int = 10):
        # Call Model layer for pagination
        return await User.page_users(name=name, page=page, page_size=page_size)

    @staticmethod
    async def update_user(user_id: int, update_data: dict):
        # Check existence - call Model layer
        user = await User.get(user_id, to_dict=False)
        if not user:
            raise BusinessException("User not found")

        # Business validation
        if "email" in update_data:
            existing = await User.get_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise BusinessException("Email already in use")

        # Update - call Model layer
        return await User.update_non_null_fields(
            {"id": user_id, **update_data},
            to_dict=True
        )
```

**Anti-Pattern - NEVER do this:**
```python
# ❌ WRONG! Service layer operating database directly
from sqlalchemy import select, and_, func
from common.utils.context import SQLAlchemySession
from common.db.sqlalchemy import async_transaction

class UserService:
    @staticmethod
    @async_transaction  # ❌ WRONG! Only Model uses this
    async def create_user(user_data: dict):
        session = SQLAlchemySession.get()  # ❌ FORBIDDEN!

        # ❌ FORBIDDEN! Direct database query
        stmt = select(User).where(
            and_(User.email == user_data["email"], User.enabled_flag == True)
        )
        result = await session.execute(stmt)  # ❌ FORBIDDEN!
        existing = result.scalar_one_or_none()

        if existing:
            raise BusinessException("User exists")

        # ❌ FORBIDDEN! Direct database insert
        user = User(**user_data)
        session.add(user)  # ❌ FORBIDDEN!
        await session.flush()
```

### Schema Layer Template

Location: `templates/schema_template.py`

Key points:
- All schemas inherit from `BaseSchema` (includes `from_attributes = True`)
- Create schema inherits from Base schema
- Update schema has all fields optional
- Response schema inherits from Base schema, adds ID and timestamp fields

### API Layer Template

Location: `templates/api_template.py`

Key points:
- Use `app.corelibs.custom_router.APIRouter` (auto-sets request context)
- Use full path in routes (e.g., `/projects`)
- Use `response_model` to specify response schema
- Use `HttpResponse.success()` for unified responses
- Delete operations use `status_code=204`

## Common Utilities

### Response Utility

Use `HttpResponse` class for unified responses:

```python
from app.utils.response import HttpResponse

# Success response
return await HttpResponse.success(data={"id": 1}, msg="操作成功")

# Error response
return await HttpResponse.fail(code=-1, msg="操作失败")
```

### Exception Handling

Use custom exception classes:

```python
from app.exceptions.exceptions import (
    BusinessException,
    ValidationException,
    IdNotExist,
    ParameterError
)

raise BusinessException("业务逻辑错误")
raise IdNotExist()
```

### Status Codes

Use `CodeEnum` for business status codes:

```python
from app.corelibs.codes import CodeEnum

code = CodeEnum.PARTNER_CODE_OK.code  # 0
msg = CodeEnum.PARTNER_CODE_OK.msg    # "OK"
```

## Usage Examples

### Generate a Complete CRUD Module

When asked to generate code for a new entity (e.g., "User"), this skill will:

1. Create Model class in `app/models/user.py` with:
   - Table definition
   - Custom query methods (get_by_status, get_data_with_pagination)
   - Proper indexes

2. Create Service class in `app/services/user_service.py` with:
   - create_user()
   - get_user()
   - page_users()
   - update_user()
   - delete_user()

3. Create Schema classes in `app/schemas/user.py` with:
   - UserBase
   - UserCreate
   - UserUpdate
   - User (response)

4. Create API routes in `app/api/v1/users.py` with:
   - POST /users
   - GET /users
   - GET /users/{id}
   - PUT /users/{id}
   - DELETE /users/{id}

### Generate Single Layer Code

You can also ask to generate only specific layers:
- "Generate Model class for User"
- "Generate Service class for User"
- "Generate API routes for User"

## Best Practices

### Model Layer
- Always include `enabled_flag == 1` in query conditions
- Use `get_table_columns()` to avoid returning model objects
- Encapsulate complex queries as class methods
- Add indexes for frequently queried fields

### Service Layer
- Only call Model layer, never direct database operations
- Implement business logic and validation
- Use appropriate exceptions
- Use static methods

### API Layer
- Use Pydantic Schema for parameter validation
- Use HttpResponse for unified responses
- Use response_model to specify response schema
- Add route tags and summaries

## Code Checklist

After generating code, verify:

### Model Layer
- [ ] Inherits from `Base` class
- [ ] Contains all business fields
- [ ] Query methods include `enabled_flag == 1` condition
- [ ] Uses `get_table_columns()` to return dictionaries
- [ ] Has necessary indexes

### Service Layer
- [ ] Only calls Model layer, no direct database operations
- [ ] Contains business logic validation
- [ ] Exception handling is correct
- [ ] Uses static methods

### Schema Layer
- [ ] Uses Pydantic BaseModel
- [ ] Fields have description and title
- [ ] Create and Update schemas are separated
- [ ] Response schema includes common fields

### API Layer
- [ ] Uses HttpResponse for responses
- [ ] Parameter validation uses Schema
- [ ] Routes have tags and summaries
- [ ] Exceptions are caught by global handler

## Common Modules

The skill includes ready-to-use common modules in the `common/` directory. All these modules are standard and can be directly imported in generated code.

### Database Connection (`common/db.py`)

```python
from app.db.sqlalchemy import async_session, async_transaction

# Base model methods are already wrapped with @async_transaction
# All database operations are automatically transactional
```

### Redis Connection (`common/redis.py`)

```python
from app.db.redis import redis_pool

# Initialize in app startup
redis_pool.init_by_config(settings)

# Use Redis
redis = redis_pool.get_redis()
await redis.set("key", {"data": "value"}, ex=3600)
data = await redis.get("key")  # Auto JSON deserialize
```

### Configuration (`common/config.py`)

```python
from app.config import settings

db_url = settings.DATABASE_URL
redis_uri = settings.REDIS_URI
debug = settings.DEBUG
```

### API Dependencies (`common/deps.py`)

```python
from app.api.deps import get_db, get_redis

# Use in FastAPI dependencies
@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    pass
```

### Exceptions (`common/exceptions.py`)

```python
from app.exceptions.exceptions import BusinessException, IdNotExist

raise BusinessException("业务逻辑错误")
raise IdNotExist()
```

### Core Libraries (`common/corelibs.py`)

```python
# Custom Router
from app.corelibs.custom_router import APIRouter

# Logger
from app.corelibs.logger import logger, init_logger

# Status Codes
from app.corelibs.codes import CodeEnum

# Local Context
from app.corelibs.local import g

# Constants
from app.corelibs.consts import DEFAULT_PAGE, CACHE_HOUR
```

### Utils (`common/utils.py`)

```python
# Response
from app.utils.response import HttpResponse

# Context
from app.utils.context import AppTraceId, SQLAlchemySession

# Serialize
from app.utils.serialize import default_serialize

# Common Utils
from app.utils.common import get_str_uuid, md5_encrypt
```

### Schemas (`common/schemas.py`)

```python
from app.schemas.common import BaseSchema

class UserBase(BaseSchema):
    name: str
```

### Application Entry (`common/main.py`)

Standard FastAPI application entry file with lifecycle management, route registration, etc.

### Base Model Usage (`common/base_model_usage.md`)

Complete Base model usage guide with all CRUD methods, examples, and best practices.

**Key Methods:**
- Query: `get()`, `get_all()`, `pagination()`
- Create: `create()`, `batch_create()`
- Update: `update()`, `update_non_null_fields()`, `update_with_conditions()`
- Delete: `delete()`, `delete_with_conditions()`

**Usage:**
```python
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    # All Base methods are available automatically
    # await User.get(id)
    # await User.create({"name": "test"})
    # await User.update({"id": 1, "name": "new"})
    # await User.delete(id)
```

See `common/usage_examples.md` and `common/imports_reference.md` for detailed usage examples.

## Reference Files

- `app/models/base.py` - Base model with all CRUD methods
- `app/models/project.py` - Example Model implementation
- `app/services/project.py` - Example Service implementation
- `app/api/v1/projects.py` - Example API implementation
- `app/schemas/project.py` - Example Schema implementation
- `app/utils/response.py` - Response utility
- `app/exceptions/exceptions.py` - Exception classes
- `app/corelibs/codes.py` - Status code definitions
- `common/db.py` - Database connection module
- `common/redis.py` - Redis connection module
- `common/config.py` - Configuration module

## Notes

- All database operations are automatically wrapped in transactions via `@async_transaction` decorator
- User IDs (`created_by`, `updated_by`) are automatically extracted from request token
- Soft delete is the default (set `enabled_flag=0`), use `_hard=True` for physical delete
- Pagination automatically reads `page` and `pageSize` from request parameters

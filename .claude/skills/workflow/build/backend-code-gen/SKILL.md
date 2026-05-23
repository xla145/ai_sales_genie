---
name: backend-code-gen
description: "Generate Spring Boot submodule backend code following the project's established architecture pattern with MyBatis Plus, Lombok, Knife4j, and Spring Security. Use this skill when the user asks to create a new business module, add CRUD endpoints, or generate backend boilerplate for the quchi-platform-admin-backend project."
---

# Backend Code Generation

## Code Standards

**All generated code must follow**: [`.claude/rules/java-code-standards.md`](../../rules/java-code-standards.md)

## Overview

Generate Spring Boot 3 submodule code that follows the project's established patterns. Every business module lives under `modules/` as an independent Maven submodule, shares entities/mappers from `generic-orm-archetype`, and exposes REST endpoints through a consistent Controller → Service → Mapper layered architecture.

## Project Architecture

**Controller → Service → Mapper (MyBatis Plus)** layered pattern:

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Controller** | `modules/{module}/src/.../controller/` | REST endpoints, input validation, response wrapping |
| **Service** | `modules/{module}/src/.../service/` | Business logic, transactions |
| **DTO/Request** | `modules/{module}/src/.../dto/request/` | Input models with validation |
| **DTO/Response** | `modules/{module}/src/.../dto/response/` | Output models |
| **Constants** | `modules/{module}/src/.../constants/` | Enum-style constants + messages |
| **Entity** | `modules/generic-orm-archetype/src/.../orm/entity/` | JPA/MyBatis entity |
| **Mapper** | `modules/generic-orm-archetype/src/.../orm/mapper/` | MyBatis Plus BaseMapper |
| **Common** | `modules/{module}/src/.../dto/response/common/` | Result<T>, PageResponse<T> |

**Base package**: `com.bytefactory.quchiv2`
**Tech Stack**: Spring Boot 3.3, MyBatis Plus 3.5.5, Lombok, Knife4j 4.4, Spring Security, Jakarta Validation

---

## Workflow

### 1) Understand Requirements

> **何时先用 `/think-code` 规划？**
> - 模块有 **多个关联实体**（非标准 1:N 子实体）→ 先规划数据模型
> - 业务逻辑**超出 CRUD**（如状态机、审批流、定时触发）→ 先规划
> - 不确定 **entity 字段设计** → 先研究数据库现有表结构
> - 标准 CRUD + 明确字段 → 直接用本 skill 生成

- Identify the **module name** (e.g., `announcement`) and **feature name** (e.g., `Announcement`)
- Identify **entity fields** and their types
- Determine **CRUD operations** needed (list/add/edit/delete/detail are standard)
- Note any **special relationships** (one-to-many, file references, enum fields)
- Check `modules/generic-orm-archetype` — entity/mapper may already exist

### 2) Plan File Set

Standard CRUD module generates these files:

```
modules/{module}/
├── pom.xml
└── src/main/java/com/bytefactory/quchiv2/{module}/
    ├── controller/{Feature}Controller.java
    ├── service/
    │   ├── {Feature}Service.java
    │   └── impl/{Feature}ServiceImpl.java
    ├── dto/
    │   ├── request/
    │   │   ├── {Feature}AddRequest.java
    │   │   ├── {Feature}EditRequest.java
    │   │   ├── {Feature}QueryRequest.java
    │   │   ├── {Feature}DeleteRequest.java
    │   │   └── {Feature}DetailRequest.java
    │   └── response/
    │       ├── {Feature}ListResponse.java
    │       ├── {Feature}DetailResponse.java
    │       └── common/
    │           ├── Result.java
    │           └── PageResponse.java
    └── constants/
        └── {Module}Constants.java

modules/generic-orm-archetype/src/main/java/com/bytefactory/quchiv2/orm/
├── entity/{Entity}.java
└── mapper/{Entity}Mapper.java
```

Trim or expand based on actual requirements.

### 3) Choose Generation Pattern

| Pattern | Use Case | Reference |
|---------|----------|-----------|
| **Standard CRUD** | List + Add + Edit + Delete + Detail | [crud-template.md](references/crud-template.md) |
| **Simple Read-only** | Dict / dropdown / display only | [crud-template.md](references/crud-template.md#read-only) |
| **With Relations** | One-to-many sub-entities (e.g., scenarios, tags) | [crud-template.md](references/crud-template.md#with-relations) |
| **Dict / Dropdown** | Static enum lookups | [constants-template.md](references/constants-template.md) |

### 4) Generate Code

**Order** (follow this to avoid missing dependencies):

1. Entity + Mapper → `generic-orm-archetype`
2. `pom.xml` for the module
3. Constants class
4. Common classes (Result, PageResponse) — copy from agreement module if they don't exist
5. DTO Request classes
6. DTO Response classes
7. Service interface
8. Service implementation
9. Controller

**References**:
- Entity + Mapper: [entity-mapper-template.md](references/entity-mapper-template.md)
- Module pom.xml: [pom-template.md](references/pom-template.md)
- Constants: [constants-template.md](references/constants-template.md)
- DTOs: [dto-templates.md](references/dto-templates.md)
- Service: [service-template.md](references/service-template.md)
- Controller: [controller-template.md](references/controller-template.md)

### 5) Generate CREATE TABLE SQL

After generating the entity, **always output the corresponding CREATE TABLE SQL** so developers can apply it to the database.

Follow the type mapping in [sql-template.md](references/sql-template.md) to convert Java fields → SQL columns.

**Required output format** (MySQL / MariaDB):

```sql
CREATE TABLE `{table_name}` (
    `id`         VARCHAR(32)   NOT NULL                COMMENT '主键ID',
    -- 业务字段 ...
    `creator`    VARCHAR(64)   DEFAULT NULL            COMMENT '创建人',
    `updater`    VARCHAR(64)   DEFAULT NULL            COMMENT '更新人',
    `create_at`  BIGINT        DEFAULT NULL            COMMENT '创建时间（毫秒时间戳）',
    `update_at`  BIGINT        DEFAULT NULL            COMMENT '更新时间（毫秒时间戳）',
    `is_delete`  VARCHAR(1)    NOT NULL DEFAULT 'N'    COMMENT '是否删除（Y=已删除,N=未删除）',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{中文表注释}';
```

**Rules**:
- Column order: `id` first → business fields → `creator/updater/create_at/update_at/is_delete` last
- Column name: camelCase Java field → snake_case SQL column (`createAt` → `create_at`)
- All columns include a `COMMENT` matching the Java field comment
- `is_delete` always `NOT NULL DEFAULT 'N'`
- `id` always `VARCHAR(32) NOT NULL`

Reference: [sql-template.md](references/sql-template.md)

---

### 6) Register Module

After generating code, register in root `pom.xml`:

1. Add `<module>modules/{module}</module>` to `<modules>` section
2. Add dependency in `<dependencyManagement>`:
```xml
<dependency>
    <groupId>com.bytefactory.quchiv2</groupId>
    <artifactId>{ArtifactId}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</dependency>
```

### 7) Verify Checklist

**Structure**:
- [ ] Entity uses `@TableName`, `@TableId(type = IdType.ASSIGN_ID)`, `@Data`
- [ ] Mapper extends `BaseMapper<Entity>`
- [ ] ServiceImpl extends `ServiceImpl<Mapper, Entity>` and implements Service
- [ ] Controller uses `@RequiredArgsConstructor`, `@Tag`, `@Operation`
- [ ] All endpoints wrapped in `try/catch` → `Result.success()` / `Result.error()`

**Fields & Conventions**:
- [ ] `id` field is `String` type with `@TableId(type = IdType.ASSIGN_ID)`
- [ ] Timestamps use `Long` (milliseconds): `createAt`, `updateAt`
- [ ] Soft delete via `isDelete` field (`"Y"` = deleted, `"N"` = not deleted)
- [ ] `creator` + `updater` fields store username (String)
- [ ] Request fields use `@JsonProperty("snake_case")` + camelCase Java name
- [ ] Query requests have `pageNum = 1` and `pageSize = 10` defaults

**Security & Logging**:
- [ ] Write operations use `@Log(title = "...", businessType = N)` annotation
  - businessType: 1=新增, 2=修改, 3=删除, 12=查询
- [ ] Current user obtained via `SecurityContextHolder` + `SysUserMapper`
- [ ] `@Transactional(rollbackFor = Exception.class)` on write methods

**API**:
- [ ] All write endpoints use `@PostMapping`; read-only dict uses `@GetMapping`
- [ ] URL pattern: `/api/{module}/{feature}/{action}`
- [ ] Pagination query uses `Page<Entity>` + `IPage<Entity>` from MyBatis Plus

**Code Generation Standards ( Step2)**:

*Must Include*:
- [ ] Complete class definitions (no missing methods)
- [ ] Proper JavaDoc comments (class-level + public methods)
- [ ] Type annotations (generics, return types explicit)
- [ ] Exception handling (BusinessException + global exception handler)
- [ ] Unit test skeleton (at least core methods)

*Must NOT Include*:
- [ ] Hardcoded magic numbers/strings
- [ ] TODO placeholders (unless annotated with acceptance criteria)
- [ ] N+1 queries (database queries inside loops)
- [ ] SQL concatenation (string concatenation for SQL)

*design.md Consistency* (if design.md exists):
- [ ] Interface definitions match design.md
- [ ] Data structures match design.md
- [ ] No undeclared dependencies introduced


---

## Design Principles

1. **Copy, Don't Invent** — follow the agreement module pattern exactly
2. **Soft Delete Always** — set `isDelete = "Y"`, never physical delete unless asked
3. **Validate at Boundary** — use `@NotNull`, `@NotBlank`, `@NotEmpty` on required request fields
4. **Constants for Magic Values** — enums, status codes, and messages go into `{Module}Constants`
5. **Transactional for Writes** — every add/edit/delete must be `@Transactional`
6. **Security Context for User** — always get current user from `SecurityContextHolder`

---

## Quick Decision Guide

```
User Request
    ↓
Has existing entity in generic-orm-archetype?
├─ Yes → Skip entity/mapper generation
└─ No → Generate entity + mapper first

Simple list/add/edit/delete/detail?
├─ Yes → crud-template.md (standard)
└─ No → Check features
    ├─ Read-only dropdown → Read-only pattern (crud-template.md#read-only)
    ├─ Sub-entities (1:N) → With-relations pattern (crud-template.md#with-relations)
    ├─ File references → Add fileMapper injection, load File entity in detail
    └─ Enum status fields → Add to Constants + provide dict endpoint

Need to register in root pom.xml?
└─ Always → Add module + dependency entries
```

---

## Reference Library

| File | Content |
|------|---------|
| **entity-mapper-template.md** | Entity class + Mapper interface templates |
| **pom-template.md** | Module pom.xml template |
| **constants-template.md** | Constants class with inner classes pattern |
| **dto-templates.md** | All request/response DTO templates |
| **service-template.md** | Service interface + ServiceImpl templates |
| **controller-template.md** | Controller with all CRUD endpoints |
| **crud-template.md** | End-to-end CRUD pattern reference |
| **sql-template.md** | Java→SQL 类型映射 + 建表语句模板 |

All patterns based on `modules/agreement/` as the canonical reference module.

---

**Remember**: The goal is **zero deviation** from established patterns. Consistency across 31 modules matters more than any individual optimization. When in doubt, copy from `modules/agreement/`.

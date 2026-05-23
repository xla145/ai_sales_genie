# 架构约束检查清单

## 1. 模块依赖方向

### Spring Boot 分层架构

| 层级 | 允许依赖 | 禁止依赖 |
|------|----------|----------|
| Controller | Service, DTO | Mapper, Entity, Repository |
| Service | Service, Mapper, Repository, Entity, DTO | Controller |
| Mapper/Repository | Entity | Controller, Service, DTO |
| Entity | 无（纯数据对象） | 任何业务层 |
| DTO | 无（纯传输对象） | 任何业务层 |

### 依赖方向规则

- ✅ 上层 → 下层：允许
- 🚫 下层 → 上层：禁止
- 🚫 跨层跳过：禁止（如 Controller → Mapper）
- ✅ 同层横向引用：谨慎允许（Service → Service）

---

## 2. 循环依赖

### 检测规则

| 模式 | 示例 | 严重级别 | 修复方案 |
|------|------|----------|----------|
| 直接循环 | A → B → A | 🚫 Critical | 提取公共模块 C |
| 间接循环 | A → B → C → A | 🚫 Critical | 引入事件/接口解耦 |
| 自依赖 | A → A | 🚫 Critical | 拆分模块职责 |

### 解耦策略

1. **提取公共模块**：将共享逻辑提取到独立的 common 模块
2. **接口倒置**：下层定义接口，上层实现（DIP）
3. **事件驱动**：使用 Spring Event 替代直接调用
4. **Facade 模式**：引入门面层隔离模块间直接依赖

---

## 3. 包结构规范

### 推荐结构：按功能分包

```
com.example.project/
├── user/                          # 用户模块
│   ├── UserController.java
│   ├── UserService.java
│   ├── UserRepository.java
│   ├── User.java
│   └── dto/
│       ├── UserCreateRequest.java
│       └── UserResponse.java
├── order/                         # 订单模块
│   ├── OrderController.java
│   ├── OrderService.java
│   ├── OrderRepository.java
│   ├── Order.java
│   └── dto/
│       └── OrderResponse.java
└── common/                        # 公共模块
    ├── exception/
    │   └── BusinessException.java
    └── util/
        └── DateUtils.java
```

### 禁止结构：按类型分包

```
🚫 com.example.project/
├── controller/
│   ├── UserController.java
│   └── OrderController.java
├── service/
│   ├── UserService.java
│   └── OrderService.java
└── repository/
    ├── UserRepository.java
    └── OrderRepository.java
```

---

## 4. 敏感操作确认

| 操作类型 | 检查点 | 确认要求 |
|----------|--------|----------|
| 数据库写操作 | INSERT/UPDATE/DELETE | 事务边界 + 权限校验 |
| 批量操作 | 无 LIMIT 的批量 SQL | 影响范围 + 分页策略 |
| DDL 变更 | ALTER/DROP TABLE | 迁移脚本 + 回滚方案 |
| 配置变更 | application*.yml | 环境差异 + 变更审批 |
| 外部调用 | HTTP/RPC 调用 | 超时设置 + 降级策略 |

---

## 5. 与 Claude Skills 配置对齐

| 检查项 | 文件来源 | 对齐要求 |
|--------|----------|----------|
| 编码规范 | .claude/rules/java-code-standards.md | 代码风格一致 |
| 安全规范 | .claude/rules/security.md | 安全编码合规 |
| 测试规范 | .claude/rules/testing.md | 覆盖率达标 |
| 架构声明 | AGENTS.md | 模块声明完整 |
| 模块设计 | design.md | 接口与实现一致 |

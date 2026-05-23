# AGENTS.md 模板



---

# AGENTS.md - [项目名称]

> 最后更新：[日期]
> 更新人：[姓名]
> 版本：v1.0

---

## 项目概述

[一句话描述项目目标]

## 技术栈

| 类型 | 技术 | 版本 |
|------|------|------|
| 后端 | Spring Boot | 3.x |
| 前端 | Vue 3 | 3.4+ |
| 数据库 | PostgreSQL | 15+ |
| 缓存 | Redis | 7+ |
| 部署 | Docker | 24+ |

## 项目结构

```
project/
├── backend/           # 后端源码
│   ├── common/        # 公共模块
│   ├── module-user/   # 用户模块
│   └── module-order/  # 订单模块
├── frontend/          # 前端源码
│   ├── src/
│   └── public/
├── docs/              # 文档
│   └── design/        # 设计文档
└── ops/               # 运维脚本
```

## 核心模块

### 用户模块 (module-user)
- **职责**：用户注册、登录、认证
- **关键接口**：POST /api/user/register, POST /api/user/login
- **设计文档**：[design.md](./docs/design/module-user/design.md)

### 订单模块 (module-order)
- **职责**：订单创建、查询、管理
- **关键接口**：POST /api/order, GET /api/order/{id}
- **设计文档**：[design.md](./docs/design/module-order/design.md)

## 架构约束

### 允许的依赖方向

```
Controller → Service → Repository
Service → Service (同一模块内)
```

### 禁止的依赖

- ❌ Repository 层直接暴露给 Controller
- ❌ 跨模块直接调用（通过接口）
- ❌ 前端直接访问数据库

## 编码规范

### 命名约定

| 语言 | 类/组件 | 方法/函数 | 变量 | 常量 | 包/目录 |
|------|---------|-----------|------|------|---------|
| Java | PascalCase | camelCase | camelCase | UPPER_SNAKE | lowercase |
| Vue | PascalCase | camelCase | camelCase | UPPER_SNAKE | kebab-case |

### 代码风格

- 格式化：使用团队统一的 formatter 配置
- 检查：必须通过 Checkstyle/ESLint

## AI 使用约束

### 三级边界

| 级别 | 规则 |
|------|------|
| ✅ **始终执行** | 遵循规范、补充注释、运行检查 |
| ⚠️ **事先询问** | 修改 design.md、引入新依赖、删除文件 |
| 🚫 **绝不执行** | 直接提交代码、暴露敏感信息 |

### 上下文来源

1. 本文件 (AGENTS.md)
2. 对应模块的 design.md
3. Claude Skills 中的规范

## 联系方式

| 角色 | 姓名 | 职责 |
|------|------|------|
| 架构师 | [姓名] | 架构设计、技术决策 |
| 技术负责人 | [姓名] | 日常开发协调 |

## 变更日志

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0 | [日期] | 初始版本 | [姓名] |

---
name: architecture-constraint-checker
description: "架构约束检查：检查代码变更是否违反模块依赖方向、循环依赖、包结构规范等架构约束。Examples: \"检查架构约束\", \"模块依赖是否合理\", \"有没有循环依赖\", \"包结构规范检查\""
version: 1.0.0
workflow_stage: "Crosscutting"
---

# 架构约束检查器

## 规范来源

> 本 Skill 基于 架构约束 (Architectural Constraints) 实现

## 触发条件

- 代码变更涉及跨模块引用或新增 import
- 新增模块/包/目录结构
- 修改模块间的依赖关系
- 重构涉及模块拆分或合并
- 代码审查时需要检查架构合规性
- CI/CD pre-commit 钩子触发

## 工作流

### Phase 1: 架构约束定义加载

从项目上下文中加载架构约束定义：

```
加载架构约束
    │
    ├── AGENTS.md → 项目级架构约束（模块划分、依赖方向）
    │
    ├── design.md → 模块级架构约束（接口定义、数据结构）
    │
    └── 约定约束 → 内置默认规则
        ├── 上层模块不得依赖下层模块
        ├── 禁止模块间循环依赖
        ├── 按功能分包，禁止按类型分包
        └── 数据库写操作需二次确认
```

### Phase 2: 模块依赖方向检查

检查变更代码的 import/依赖是否违反分层架构：

```
分层架构依赖方向（自上而下）：

  Controller 层
       ↓ 可依赖
  Service 层
       ↓ 可依赖
  Repository/Mapper 层
       ↓ 可依赖
  Entity/Model 层

规则：
  ✅ 上层依赖下层 → 允许
  🚫 下层依赖上层 → 禁止
  🚫 跨层依赖（如 Controller 直接依赖 Mapper）→ 禁止
  🚫 同层循环依赖 → 禁止
```

| 检查项 | 违规模式 | 严重级别 |
|--------|----------|----------|
| Controller → Service | Controller 直接 import Mapper/Repository | 🚫 Critical |
| Service → Repository | Service 直接 import Controller | 🚫 Critical |
| Repository → Entity | Repository import Service | 🚫 Critical |
| 跨层调用 | 跳过中间层直接调用底层 | ⚠️ Warning |
| 反向依赖 | 下层 import 上层 | 🚫 Critical |

### Phase 3: 循环依赖检测

扫描变更涉及的模块间是否存在循环依赖：

```
循环依赖检测
    │
    ├── 直接循环：A → B → A
    │   └── 🚫 Critical：必须立即解除
    │
    ├── 间接循环：A → B → C → A
    │   └── 🚫 Critical：必须立即解除
    │
    └── 无循环
        └── ✅ Pass
```

| 检查项 | 说明 | 严重级别 |
|--------|------|----------|
| 直接循环依赖 | 两个模块互相 import | 🚫 Critical |
| 间接循环依赖 | 三个及以上模块形成环 | 🚫 Critical |
| 共享依赖 | 多个模块依赖同一工具类 | ✅ Info |

### Phase 4: 包结构规范检查

检查包/目录结构是否符合按功能分包原则：

```
包结构规范
    │
    ├── ✅ 按功能分包（推荐）
    │   └── com.example.user/
    │       ├── UserController.java
    │       ├── UserService.java
    │       ├── UserRepository.java
    │       └── User.java
    │
    └── 🚫 按类型分包（禁止）
        └── com.example/
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

| 检查项 | 违规模式 | 严重级别 |
|--------|----------|----------|
| 按类型分包 | 同一类型文件集中在一个包下 | ⚠️ Warning |
| 功能内聚 | 同一功能的文件分散在不同包下 | ⚠️ Warning |
| 包命名规范 | 包名含大写字母或特殊字符 | ⚠️ Warning |
| 深层嵌套 | 包层级超过 5 层 | ℹ️ Info |

### Phase 5: 敏感操作检查

检查代码变更是否涉及需要二次确认的敏感操作：

| 敏感操作 | 检查内容 | 处理方式 |
|----------|----------|----------|
| 数据库写操作 | INSERT/UPDATE/DELETE 语句 | 需确认事务边界和权限校验 |
| 批量操作 | 批量更新/删除（无 LIMIT） | 需确认影响范围 |
| DDL 变更 | ALTER/DROP TABLE | 需确认迁移脚本和回滚方案 |
| 配置变更 | 修改 application.yml 等配置 | 需确认环境影响 |

### Phase 6: 与 Claude Skills 配置对齐

检查代码变更是否与项目中的 Claude Skills 配置保持一致：

| 检查项 | 说明 | 严重级别 |
|--------|------|----------|
| Skills 约束遵守 | 代码是否遵守 Skills 中定义的编码规范 | ⚠️ Warning |
| 架构约束定义 | 新增模块是否在 AGENTS.md 中声明 | ⚠️ Warning |
| 依赖声明 | 新增外部依赖是否在 design.md 中说明 | ⚠️ Warning |

### Phase 7: 输出报告

```markdown
## 🏗️ 架构约束检查报告

**检查范围**：[变更文件列表]
**检查结果**：[通过 ✅ / 警告 ⚠️ / 阻断 🚫]

### 1. 模块依赖方向

| # | 级别 | 源模块 | 目标模块 | 违规描述 | 建议 |
|---|------|--------|----------|----------|------|
| 1 | 🚫 | Controller | Mapper | 跨层直接依赖 | 通过 Service 层间接调用 |

### 2. 循环依赖

| # | 级别 | 依赖链 | 描述 | 建议 |
|---|------|--------|------|------|
| 1 | 🚫 | A → B → A | 直接循环 | 提取公共模块或使用事件解耦 |

### 3. 包结构规范

| # | 级别 | 当前结构 | 推荐结构 | 描述 |
|---|------|----------|----------|------|
| 1 | ⚠️ | 按类型分包 | 按功能分包 | 建议迁移为功能包结构 |

### 4. 敏感操作

| # | 操作类型 | 位置 | 影响范围 | 需确认项 |
|---|----------|------|----------|----------|
| 1 | 数据库写操作 | file:line | 全表更新 | 事务边界 + 权限校验 |

### 5. 与 Skills 配置对齐

| # | 检查项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | 编码规范遵守 | ✅ | 符合 java-code-standards |
| 2 | AGENTS.md 声明 | ⚠️ | 新增模块未在 AGENTS.md 中声明 |

### 修复建议

- 🚫 Critical 问题：**必须修复后才能合并**
- ⚠️ Warning 问题：建议修复，可录入技术债务登记册
```

## 输入

| 输入项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| 变更文件 | 文件列表 | 是 | 需要检查的代码文件 |
| 检查模式 | 枚举 | 否 | full（完整检查）/ dependency（仅依赖检查）/ structure（仅包结构检查）/ sensitive（仅敏感操作检查），默认 full |
| 项目架构定义 | 文件引用 | 否 | AGENTS.md 或 design.md 路径，用于加载架构约束 |

## 输出

| 输出项 | 格式 | 说明 |
|--------|------|------|
| 检查判定 | ✅/⚠️/🚫 | 通过/警告/阻断 |
| 依赖方向报告 | 表格 | 模块依赖方向违规 |
| 循环依赖报告 | 表格 | 循环依赖检测结果 |
| 包结构报告 | 表格 | 包结构规范检查结果 |
| 敏感操作报告 | 表格 | 敏感操作确认清单 |
| 修复建议 | 文本 | 各类问题的修复方案 |

## 检查清单

- [ ] 变更代码的 import 是否违反分层架构？
- [ ] 是否存在模块间循环依赖？
- [ ] 包结构是否符合按功能分包原则？
- [ ] 是否涉及数据库写操作？是否需要二次确认？
- [ ] 新增模块是否在 AGENTS.md 中声明？
- [ ] 新增依赖是否在 design.md 中说明？
- [ ] 代码是否遵守项目 Claude Skills 中定义的规范？

## 与其他 Skills 的关系

| 关联 Skill | 关系类型 | 说明 |
|------------|----------|------|
| boundary-enforcer | 前置 | boundary-enforcer 判定架构类操作后，由本 Skill 深度检查 |
| code-generation-standard | 协同 | 代码生成后由本 Skill 执行架构约束检查 |
| code-review-expert | 协同 | 代码审查中的架构维度由本 Skill 提供 |
| data-security-guard | 协同 | 敏感操作检查可联动数据安全守卫 |
| design-doc-generator | 上游 | design.md 定义了架构约束，本 Skill 负责执行检查 |
| agents-md-updater | 上游 | AGENTS.md 声明了项目架构，本 Skill 对齐检查 |

## 参考资源

- [架构约束检查清单](checklists/architecture-constraint-checklist.md)

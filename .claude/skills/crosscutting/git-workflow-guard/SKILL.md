---
name: git-workflow-guard
description: "Git 工作流守卫：统一 Git 分支命名、Commit 规范、MR 流程检查，防止违规操作。Examples: \"检查 Git 工作流\", \"分支命名是否规范\", \"commit 规范检查\", \"MR 提交前检查\""
version: 1.0.0
workflow_stage: "Crosscutting"
---

# Git 工作流守卫

## 规范来源

> 本 Skill 基于 项目与版本控制规范实现

## 触发条件

- 创建新分支时
- 执行 git commit 时
- 提交 MR 前检查
- 直接 push 到受保护分支时
- 用户询问 Git 操作是否合规

## 工作流

### Phase 1: 分支命名规范检查

检查分支名称是否符合  规范：

```
分支命名检查
    │
    ├── main / develop → ✅ 长期分支，无需检查
    │
    ├── feature/* → 检查格式
    │   ├── ✅ feature/TB1234-user-login
    │   ├── 🚫 feature/user-login（缺少 TB 号）
    │   └── 🚫 feature-TB1234-user-login（分隔符错误）
    │
    ├── release/* → 检查格式
    │   ├── ✅ release/v1.1.0
    │   └── 🚫 release/1.1.0（缺少 v 前缀）
    │
    ├── hotfix/* → 检查格式
    │   ├── ✅ hotfix/TB1235-fix-login
    │   ├── 🚫 hotfix/fix-login（缺少 TB 号）
    │   └── 🚫 hotfix-TB1235-fix-login（分隔符错误）
    │
    └── 其他 → 🚫 不符合规范的分支类型
```

| 分支类型 | 命名规范 | 来源 | 合并去向 | 生命周期 |
|----------|----------|------|----------|----------|
| main | - | - | - | 长期 |
| develop | - | main | - | 长期 |
| feature | `feature/TB号-描述` | develop | develop | MR 后删除 |
| release | `release/v版本号` | develop | main → develop | MR 后删除 |
| hotfix | `hotfix/TB号-描述` | main | main → develop | MR 后删除 |

### Phase 2: Commit 规范检查

检查 commit message 是否符合  Conventional Commits：

```
Commit 规范检查
    │
    ├── 格式检查：<type>(<scope>): <subject>
    │   ├── ✅ feat(user): 新增用户注册功能
    │   ├── 🚫 新增用户注册功能（缺少 type 和 scope）
    │   └── 🚫 feat: 新增用户注册功能（缺少 scope）
    │
    ├── Type 检查
    │   ├── ✅ feat / fix / docs / style / refactor / perf / test / chore
    │   ├── ⚠️ wip（仅限个人分支，禁止出现在 MR 中）
    │   └── 🚫 其他非标准 type
    │
    └── TB 号关联检查
        ├── ✅ body 或 footer 包含 Closes #TB号 或 Refs #TB号
        └── ⚠️ 未关联 TB 任务号
```

| Type | 说明 | MR 中允许 |
|------|------|-----------|
| feat | 新功能 | ✅ |
| fix | Bug 修复 | ✅ |
| docs | 文档更新 | ✅ |
| style | 格式调整 | ✅ |
| refactor | 重构 | ✅ |
| perf | 性能优化 | ✅ |
| test | 测试相关 | ✅ |
| chore | 构建/工具 | ✅ |
| wip | 工作进行中 | 🚫 禁止 |

### Phase 3: MR 提交前检查

提交 MR 前执行完整性检查：

```
MR 提交前检查
    │
    ├── 1. wip commits 清理
    │   ├── 检查：git log develop..HEAD --oneline
    │   ├── 有 wip commits → 🚫 需要交互式变基清理
    │   └── 无 wip commits → ✅ 通过
    │
    ├── 2. 分支同步检查
    │   ├── feature 分支是否基于最新 develop？
    │   ├── 否 → ⚠️ 需要 git rebase develop
    │   └── 是 → ✅ 通过
    │
    ├── 3. 代码审查准备
    │   ├── 变更文件数量合理？
    │   ├── commit 数量合理（建议 ≤ 10）？
    │   └── MR 描述是否完整？
    │
    └── 4. TB 号关联
        ├── MR 标题是否包含 TB 号？
        ├── MR 描述是否关联 TB 任务？
        └── commit 是否关联 TB 号？
```

### Phase 4: 受保护分支操作检查

检查是否违反受保护分支规则：

```
受保护分支检查
    │
    ├── 直接 push 到 main → 🚫 绝对禁止
    ├── 直接 push 到 develop → 🚫 必须通过 MR
    ├── 绕过代码审查合并 → 🚫 绝对禁止
    ├── 强制 push 到任何分支 → 🚫 绝对禁止
    │
    ├── feature → develop 合并 → ✅ 通过 MR
    ├── release → main 合并 → ✅ 通过 MR（需架构师审批）
    └── hotfix → main 合并 → ✅ 通过 MR
```

| 操作 | 判定 | 说明 |
|------|------|------|
| 直接 push main | 🚫 Never | 必须通过 release/hotfix MR |
| 直接 push develop | 🚫 Never | 必须通过 feature MR |
| force push 任何分支 | 🚫 Never | 禁止强制推送 |
| 绕过代码审查合并 | 🚫 Never | 必须至少 1 人审查 |

### Phase 5: 版本号规范检查

检查版本标签是否符合  语义化版本号：

```
版本号检查
    │
    ├── 格式：v<major>.<minor>.<patch>
    │   ├── ✅ v1.0.0
    │   ├── ✅ v2.1.3
    │   └── 🚫 1.0（缺少 v 前缀和 patch）
    │
    ├── 预发布标签
    │   ├── ✅ v1.0.0-beta.1
    │   ├── ✅ v1.0.0-rc.1
    │   └── 🚫 v1.0.0-beta（缺少预发布序号）
    │
    └── 版本递进规则
        ├── Patch：Bug 修复 → v1.0.0 → v1.0.1
        ├── Minor：新功能 → v1.0.0 → v1.1.0
        └── Major：重大变更 → v1.0.0 → v2.0.0
```

### Phase 6: 输出报告

```markdown
## 🔀 Git 工作流检查报告

**检查范围**：[分支/commit/MR]
**检查结果**：[通过 ✅ / 警告 ⚠️ / 阻断 🚫]

### 1. 分支命名

| # | 级别 | 分支名 | 问题 | 建议 |
|---|------|--------|------|------|
| 1 | 🚫 | feature/user-login | 缺少 TB 号 | feature/TB1234-user-login |

### 2. Commit 规范

| # | 级别 | Commit | 问题 | 建议 |
|---|------|--------|------|------|
| 1 | ⚠️ | abc1234 | 未关联 TB 号 | 添加 Closes #TB号 |

### 3. MR 准备

| # | 检查项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | wip commits 清理 | ✅ | 无 wip commits |
| 2 | 分支同步 | ⚠️ | 需要基于最新 develop rebase |
| 3 | TB 号关联 | ✅ | MR 标题和描述已关联 |

### 4. 受保护分支

| # | 操作 | 判定 | 说明 |
|---|------|------|------|
| 1 | push main | 🚫 | 禁止直接推送 |
```

## 输入

| 输入项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| 检查模式 | 枚举 | 否 | branch（分支命名）/ commit（commit 规范）/ mr（MR 提交前）/ protected（受保护分支）/ version（版本号）/ full（完整检查），默认 full |
| 目标分支 | 文本 | 否 | 要检查的分支名称 |
| commit 范围 | 文本 | 否 | 要检查的 commit 范围（如 develop..HEAD） |

## 输出

| 输出项 | 格式 | 说明 |
|--------|------|------|
| 检查判定 | ✅/⚠️/🚫 | 通过/警告/阻断 |
| 分支命名报告 | 表格 | 分支命名规范检查结果 |
| Commit 规范报告 | 表格 | commit message 规范检查结果 |
| MR 准备报告 | 表格 | MR 提交前检查结果 |
| 受保护分支报告 | 表格 | 受保护分支操作检查结果 |
| 修复建议 | 文本 | 各类问题的修复方案 |

## 检查清单

- [ ] 分支命名是否包含 TB 号？
- [ ] 分支类型是否为 feature/release/hotfix？
- [ ] commit message 是否符合 Conventional Commits？
- [ ] commit 是否关联了 TB 号？
- [ ] MR 中是否包含 wip commits？
- [ ] 分支是否基于最新的 develop？
- [ ] 是否尝试直接 push 受保护分支？
- [ ] 版本号是否符合语义化版本规范？

## 与其他 Skills 的关系

| 关联 Skill | 关系类型 | 说明 |
|------------|----------|------|
| boundary-enforcer | 协同 | boundary-enforcer 判定 Git 类操作后，由本 Skill 深度检查 |
| git-feature | 前置 | 创建 feature 分支时由本 Skill 校验命名 |
| git-hotfix | 前置 | 创建 hotfix 分支时由本 Skill 校验命名 |
| git-release | 前置 | 发布时由本 Skill 校验版本号 |
| git-merge-feature | 前置 | 合并前由本 Skill 执行 MR 检查 |
| commit | 前置 | 提交时由本 Skill 校验 commit 规范 |
| code-review-expert | 协同 | MR 门禁由 code-review-expert 执行代码审查 |

## 参考资源

- [Git 工作流检查清单](checklists/git-workflow-checklist.md)

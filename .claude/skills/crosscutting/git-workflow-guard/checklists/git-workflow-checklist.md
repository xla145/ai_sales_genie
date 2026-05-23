# Git 工作流检查清单

## 1. 分支命名

| 分支类型 | 命名格式 | 示例 |
|----------|----------|------|
| feature | `feature/TB号-描述` | `feature/TB1234-user-login` |
| release | `release/v版本号` | `release/v1.1.0` |
| hotfix | `hotfix/TB号-描述` | `hotfix/TB1235-fix-login` |

### 命名规则

- TB 号格式：TB + 数字（如 TB1234）
- 描述使用 kebab-case（小写 + 短横线）
- 分支类型与 TB 号之间用 `/` 分隔
- TB 号与描述之间用 `-` 分隔

---

## 2. Commit 规范

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 列表

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
| wip | 工作进行中 | 🚫 禁止出现在 MR |

### TB 号关联

- 在 body 或 footer 中使用 `Closes #TB号` 或 `Refs #TB号`
- 示例：`Closes #TB1234`

---

## 3. MR 提交前

| 检查项 | 命令 | 通过标准 |
|--------|------|----------|
| wip commits | `git log develop..HEAD --oneline` | 无 wip 类型 |
| 分支同步 | `git log develop..HEAD --oneline` | 基于最新 develop |
| 变更范围 | `git diff --stat develop` | 变更文件合理 |
| TB 号关联 | MR 标题/描述 | 包含 TB 号 |

### wip commits 清理

```bash
# 交互式变基清理 wip commits
git rebase -i develop

# 在编辑器中将 wip 行改为 s（squash）
```

---

## 4. 受保护分支

| 操作 | 判定 | 替代方案 |
|------|------|----------|
| 直接 push main | 🚫 禁止 | 通过 release/hotfix MR |
| 直接 push develop | 🚫 禁止 | 通过 feature MR |
| force push 任何分支 | 🚫 禁止 | 无替代 |
| 绕过代码审查合并 | 🚫 禁止 | 必须至少 1 人审查 |

---

## 5. 版本号规范

### 格式

```
v<major>.<minor>.<patch>[-<prerelease>.<number>]
```

### 示例

| 类型 | 示例 | 说明 |
|------|------|------|
| 正式版 | v1.0.0 | 生产发布 |
| Beta | v1.0.0-beta.1 | 内部测试 |
| RC | v1.0.0-rc.1 | 发布候选 |

### 递进规则

| 变更类型 | 版本递进 | 示例 |
|----------|----------|------|
| Bug 修复 | Patch +1 | v1.0.0 → v1.0.1 |
| 新功能 | Minor +1 | v1.0.0 → v1.1.0 |
| 重大变更 | Major +1 | v1.0.0 → v2.0.0 |

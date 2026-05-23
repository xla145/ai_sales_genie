---
name: git-feature
description: "Use when creating a new feature development branch. Follows the Git workflow spec: feature branches are created from main, used for development, then merged back to release via PR/MR for testing. Examples: \"Create a feature branch for user login\", \"Start a new feature branch\", \"创建功能分支\""
version: 2.0.0
---

# Git Feature Branch

Create a new feature branch following the project's Git workflow specification.

## Workflow

```
main -> feature/* -> release -> main
```

## Commands

### Create a feature branch

```bash
git checkout main
git pull origin main
git checkout -b feature/<name>
```

Example:
```bash
git checkout main
git pull origin main
git checkout -b feature/register-channel
```

### After development

1. Commit and push your changes:
```bash
git add .
git commit -m "feat: description of changes"
git push origin feature/<name>
```

2. Create a PR/MR to merge into `release`

3. After testing in `release`, merge `release` to `main`

4. Create release tag on `main`

## Branch Rules

| Rule | Description |
|------|-------------|
| Source branch | Must create from `main` |
| Target branch | Merge to `release` via PR/MR |
| Direct push | Allowed on feature branch |
| Naming | `feature/TB号-描述` |
| TB 号关联 | 分支名必须包含 TB 任务号 |
| Commit 关联 | commit message body/footer 必须关联 TB 号 |

## TB 号命名规范

分支命名格式：`feature/TB<数字>-<kebab-case描述>`

| 示例 | 是否合规 | 说明 |
|------|----------|------|
| `feature/TB1234-user-login` | ✅ | 标准格式 |
| `feature/user-login` | 🚫 | 缺少 TB 号 |
| `feature-TB1234-user-login` | 🚫 | 分隔符错误，应为 `/` |
| `feature/TB1234-user_login` | 🚫 | 描述应使用 kebab-case |

创建分支时，**必须**询问用户 TB 任务号，确保分支命名合规。

## Commit TB 号关联

提交代码时，commit message 的 body 或 footer 中必须关联 TB 号：

```bash
git commit -m "feat(user): 实现用户登录功能

- 支持手机号+验证码登录
- 支持密码登录

Closes #TB1234"
```

| 关联方式 | 示例 | 说明 |
|----------|------|------|
| Closes | `Closes #TB1234` | 完成该任务 |
| Refs | `Refs #TB1234` | 关联该任务 |

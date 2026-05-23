---
name: git-hotfix
description: "Use when creating a hotfix branch for urgent production issues. Follows the Git workflow spec: hotfix branches are created from main, fixed, merged back to main with patch tag, then synced to release. Examples: \"Create a hotfix for login bug\", \"紧急修复线上问题\", \"Hotfix production issue\""
version: 2.0.0
---

# Git Hotfix Branch

Create a hotfix branch for urgent production issue fixes.

## Workflow

```
main -> hotfix/* -> main -> tag -> release
```

**Important**: Hotfix branches must be created from `main`, not `release`.

## Commands

### Create a hotfix branch

```bash
git checkout main
git pull origin main
git checkout -b hotfix/<name>
```

Example:
```bash
git checkout main
git pull origin main
git checkout -b hotfix/TB1235-fix-login-null-pointer
```

### After fix is complete

1. Commit and push:
```bash
git add .
git commit -m "fix: description of the fix"
git push origin hotfix/<name>
```

2. Merge back to `main` via PR/MR

3. Create patch version tag on `main`:
```bash
git checkout main
git pull origin main
git tag -a v1.0.1 -m "hotfix v1.0.1"
git push origin v1.0.1
```

4. **Sync back to release** to prevent future releases from overwriting the fix:
```bash
git checkout release
git pull origin release
git merge main
git push origin release
```

## Branch Rules

| Rule | Description |
|------|-------------|
| Source branch | Must create from `main` (production) |
| Target branch | Merge to `main` via PR/MR |
| Sync required | Must sync back to `release` after fix |
| Naming | `hotfix/TB号-描述` |
| TB 号关联 | 分支名必须包含 TB 任务号 |
| Commit 关联 | commit message body/footer 必须关联 TB 号 |
| Tag type | Patch version increment |

## TB 号命名规范

分支命名格式：`hotfix/TB<数字>-<kebab-case描述>`

| 示例 | 是否合规 | 说明 |
|------|----------|------|
| `hotfix/TB1235-fix-login` | ✅ | 标准格式 |
| `hotfix/fix-login` | 🚫 | 缺少 TB 号 |
| `hotfix-TB1235-fix-login` | 🚫 | 分隔符错误，应为 `/` |

创建分支时，**必须**询问用户 TB 任务号，确保分支命名合规。

## Commit TB 号关联

提交代码时，commit message 的 body 或 footer 中必须关联 TB 号：

```bash
git commit -m "fix(login): 修复登录空指针异常

- 问题：用户信息为空时抛出 NullPointerException
- 原因：未做 null 检查
- 解决：增加 null 安全检查

Closes #TB1235"
```

---
name: git-merge-feature
description: "Use when merging a completed feature branch to release for testing. Follows the Git workflow spec: feature branches merge to release via PR/MR for testing before final release. Examples: \"Merge feature to release\", \"合并功能分支到release\", \"Submit feature for testing\""
version: 2.0.0
---

# Git Merge Feature to Release

Merge a completed feature branch to `release` for testing and validation.

## Workflow

```
feature/* --[PR/MR]--> release --[testing]--> main
```

## Commands

### Before merging - sync with latest release

```bash
# Update your feature branch with latest release changes
git checkout feature/<name>
git fetch origin release
git rebase origin/release
```

Or use merge instead of rebase (per team preference):
```bash
git merge origin/release
```

### Create PR/MR to release

Push your feature branch and create a Pull Request / Merge Request:

```bash
git push origin feature/<name> -f  # -f if rebased
```

Then create PR/MR through Git platform (GitHub/GitLab):
- **Source**: `feature/<name>`
- **Target**: `release`
- **Title**: Concise description
- **Description**: Summary of changes

### After PR/MR is merged

```bash
# Delete local feature branch (optional)
git branch -d feature/<name>

# Delete remote feature branch (optional)
git push origin --delete feature/<name>
```

## Requirements

| Requirement | Description |
|-------------|-------------|
| Code Review | Must pass review before merging |
| CI Checks | All CI checks must pass |
| Self-review | Sync with latest `release` before PR |
| Naming | PR title should follow commit convention |
| TB 号关联 | MR 标题和描述必须关联 TB 任务号 |
| wip 清理 | MR 中不得包含 wip 类型 commit |

## TB 号关联规范

### MR 标题格式

```
feat(<scope>): <描述> #TB号
```

示例：
```
feat(user): 实现用户登录功能 #TB1234
fix(order): 修复订单金额计算错误 #TB1235
```

### MR 描述模板

```markdown
## 关联任务
Closes #TB1234

## 变更说明
- [变更内容 1]
- [变更内容 2]

## 测试情况
- [x] 单元测试通过
- [x] 本地验证通过
```

### wip Commits 清理

提交 MR 前，必须清理 wip commits：

```bash
# 查看本分支相对 develop 的所有提交
git log develop..HEAD --oneline

# 交互式变基，将 wip 提交 squash 或 reword
git rebase -i develop
```

## Commit Convention (for PR title)

| Type | Prefix | Example |
|------|--------|---------|
| New feature | `feat:` | `feat: add user registration` |
| Bug fix | `fix:` | `fix: correct login validation` |
| Refactor | `refactor:` | `refactor: simplify auth flow` |
| Docs | `docs:` | `docs: update API documentation` |

## Testing Flow

After merge to `release`:

1. **Deploy** to test environment
2. **Functional testing** by QA team
3. **Integration testing** with other services
4. **User acceptance** validation
5. Once approved → merge `release` to `main` (`/git-release`)

## Example Complete Flow

```bash
# 1. Sync feature branch with latest release
git checkout feature/user-profile
git fetch origin release
git rebase origin/release

# 2. Push and create PR/MR
git push origin feature/user-profile -f

# 3. After PR/MR is merged and tested
git branch -d feature/user-profile
git checkout main
git pull origin main
```

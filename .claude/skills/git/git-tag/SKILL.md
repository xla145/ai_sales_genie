---
name: git-tag
description: "Use when creating Git tags for version releases. Follows the Git workflow spec with semantic versioning. Examples: \"Create tag v1.2.0\", \"打版本标签\", \"Tag this release\""
version: 2.0.0
---

# Git Tag

Create version tags following the project's Git workflow specification.

## Tag Naming Convention

**Semantic Versioning**: `v<major>.<minor>.<patch>`

| Type | Format | Example | When to use |
|------|--------|---------|-------------|
| **Official** | `v1.2.0` | v1.2.0, v2.0.0 | Formal releases on `main` |
| **Beta** | `v1.2.0-beta.1` | v1.2.0-beta.1 | Testing versions |
| **RC** | `v1.2.0-rc.1` | v1.2.0-rc.1 | Release candidates |

## Commands

### Create official release tag (on main)

```bash
git checkout main
git pull origin main
git tag -a v<version> -m "release v<version>"
git push origin v<version>
```

Example:
```bash
git tag -a v1.2.0 -m "release v1.2.0"
git push origin v1.2.0
```

### Create pre-release tag (on release)

```bash
git checkout release
git pull origin release
git tag -a v<version>-<suffix> -m "<type> v<version>-<suffix>"
git push origin v<version>-<suffix>
```

Examples:
```bash
# Beta
git tag -a v1.2.0-beta.1 -m "beta v1.2.0-beta.1"
git push origin v1.2.0-beta.1

# Release Candidate
git tag -a v1.2.0-rc.1 -m "release candidate v1.2.0-rc.1"
git push origin v1.2.0-rc.1
```

## Tag Type Requirements

**Use annotated tags** (recommended):
```bash
git tag -a v1.2.0 -m "release v1.2.0"
```

**Avoid lightweight tags** (not recommended):
```bash
git tag v1.2.0  # Missing metadata
```

Annotated tags include:
- Creator information
- Creation timestamp
- Tag message
- Better for audit and traceability

## Rules

| Rule | Description |
|------|-------------|
| Branch | Official tags on `main`, pre-release on `release` |
| Format | Must follow `v<major>.<minor>.<patch>` |
| Type | Use annotated tags (`-a` flag) |
| Immutability | Never modify or reuse published tags |
| Naming | Avoid meaningless names like `test`, `final`, `aaa` |
| TB 号关联 | Tag message 建议包含关联的 TB 号 |

## TB 号关联规范

创建标签时，建议在 tag message 中关联 TB 号：

```bash
git tag -a v1.2.0 -m "release v1.2.0

Features: TB1234-user-login, TB1235-order-export
Fixes: TB1236-fix-payment-timeout"
```

| 场景 | TB 号关联方式 |
|------|----------------|
| 正式发版 | tag message 列出本次包含的 TB 号 |
| 热修复 | tag message 列出修复的 TB 号 |

## List existing tags

```bash
# List all tags
git tag

# Show tag details
git show v1.2.0

# List tags with messages
git tag -n9
```

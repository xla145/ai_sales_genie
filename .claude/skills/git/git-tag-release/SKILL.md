---
name: git-tag-release
description: "Use when creating pre-release tags on the release branch for testing and validation. Follows the Git workflow spec: beta and rc tags are created on release branch before final release. Examples: \"Tag release candidate\", \"打rc标签\", \"Create beta tag on release\""
version: 2.0.0
---

# Git Tag Release (Pre-release)

Create pre-release tags (beta/rc) on the `release` branch for testing and validation.

## Workflow

```
feature/* -> release --[beta/rc tag]--> [testing]--> main --[official tag]
```

## Tag Types for Release Branch

| Type | Format | Usage |
|------|--------|-------|
| **Beta** | `v1.2.0-beta.1` | Initial testing versions |
| **RC** | `v1.2.0-rc.1` | Release candidates, nearly final |

## Commands

### Create beta tag (early testing)

```bash
git checkout release
git pull origin release
git tag -a v<version>-beta.<n> -m "beta v<version>-beta.<n>"
git push origin v<version>-beta.<n>
```

Example:
```bash
git tag -a v1.2.0-beta.1 -m "beta v1.2.0-beta.1"
git push origin v1.2.0-beta.1
```

### Create release candidate tag (ready for production)

```bash
git checkout release
git pull origin release
git tag -a v<version>-rc.<n> -m "release candidate v<version>-rc.<n>"
git push origin v<version>-rc.<n>
```

Example:
```bash
git tag -a v1.2.0-rc.1 -m "release candidate v1.2.0-rc.1"
git push origin v1.2.0-rc.1
```

### List existing pre-release tags

```bash
# Show all tags
git tag

# Show only pre-release tags
git tag | grep -E "(beta|rc)"

# Show tag details
git show v1.2.0-rc.1
```

## Version Number Pattern

```
v<major>.<minor>.<patch>-<type>.<sequence>
```

Examples:
| Tag | Version | Type | Sequence |
|-----|---------|------|----------|
| v1.2.0-beta.1 | 1.2.0 | beta | 1st beta |
| v1.2.0-beta.2 | 1.2.0 | beta | 2nd beta (after fixes) |
| v1.2.0-rc.1 | 1.2.0 | rc | 1st release candidate |
| v1.2.0-rc.2 | 1.2.0 | rc | 2nd release candidate |

## When to Use Each Type

| Type | When |
|------|------|
| **beta** | Initial feature integration, needs testing |
| **rc** | All features done, ready for final validation |
| **no suffix** | (Official tag, use `/git-tag` on main) |

## Testing Flow After Tag

1. **Deploy** the tagged version to test environment
2. **QA testing** - functional, regression, integration
3. **Bug fixes** if found → merge fixes → increment tag number
4. **Pass validation** → proceed to `/git-release` for official release

## Example Complete Pre-release Process

```bash
# First beta for testing
git tag -a v1.2.0-beta.1 -m "beta v1.2.0-beta.1"
git push origin v1.2.0-beta.1

# Testing found bugs, after fixes:
git tag -a v1.2.0-beta.2 -m "beta v1.2.0-beta.2"
git push origin v1.2.0-beta.2

# Testing passed, create release candidate
git tag -a v1.2.0-rc.1 -m "release candidate v1.2.0-rc.1"
git push origin v1.2.0-rc.1

# Final validation passed → official release on main
# Use /git-release or /git-tag on main branch
```

## Delete Pre-release Tag (if needed)

```bash
# Delete local tag
git tag -d v1.2.0-beta.1

# Delete remote tag
git push origin :refs/tags/v1.2.0-beta.1
```

**Note**: Only pre-release tags can be deleted. Official tags on `main` should never be modified.

## Differences from Official Tags

| | Pre-release (this skill) | Official (`/git-tag`) |
|---|---|---|
| **Branch** | `release` | `main` |
| **Tag suffix** | `-beta.n` or `-rc.n` | No suffix |
| **Purpose** | Testing/validation | Production release |
| **Can delete** | Yes (if wrong) | Never |
| **TB 号关联** | tag message 建议包含 TB 号 | tag message 必须包含 TB 号 |

## TB 号关联规范

创建预发布标签时，建议在 tag message 中关联 TB 号：

```bash
git tag -a v1.2.0-beta.1 -m "beta v1.2.0-beta.1

Includes: TB1234, TB1235"
```

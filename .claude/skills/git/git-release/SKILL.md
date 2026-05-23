---
name: git-release
description: "将已选中的多个功能分支合并到 release；合并前校验各分支最新代码已先进入 test，否则禁止合并。正式发版时再将 release 合并到 main 并打标签。Examples: \"合并功能分支到 release\", \"Release version 1.2.0\", \"正式发布新版本\""
version: 2.0.0
---

# Git Release（合并功能分支 → release + 正式发版）

本技能包含两段流程：

1. **合并功能分支到 `release`**（可多选）：合并前必须校验每个功能分支的**最新提交**已出现在 `test` 分支历史中；否则**不得**合并到 `release`，并明确提醒原因。
2. **正式发版**：在 `release` 验证通过后，将 `release` 合并到 `main` 并打发布标签。

## 总览

```
feature/* --[须先进入 test]--> 校验通过 --> merge --> release --[验证]--> main -> tag
```

- **test**：功能分支代码应先合并到 `test` 做联调/验证；未进 `test` 的「最新代码」不允许直接进 `release`。
- **release**：集成测试环境；可一次选择多个 `feature/*` 合并进来。

---

## 一、合并多个功能分支到 `release`

### 1. 更新远端引用

```bash
git fetch origin
```

### 2. 对每个待合并的功能分支做门禁（必做）

对**每一个**用户选中的分支 `feature/<name>`，执行：

```bash
# 若 feature/<name> 的最新提交是 origin/test 的祖先，说明该分支当前 tip 已包含在 test 历史中 → 允许进 release
git merge-base --is-ancestor origin/feature/<name> origin/test
```

- **退出码为 0**：该功能分支最新代码已在 `test` 中，**可以**合并到 `release`。
- **退出码非 0**：该功能分支相对于 `test` 仍有未纳入的提交，**禁止**合并到 `release`。提醒用户先合并到 `test`（或 rebase/merge 使 `test` 包含该分支 tip），再操作 `release`。

**注意**：若团队向 `test` 采用 **squash merge**，`feature` 上的原提交可能不在 `test` 历史里，上述祖先检测会为失败。此时应改用团队约定的校验方式（例如在平台上确认「对应 PR 已合入 test」），或保证合入 `test` 时保留分支合并历史（merge commit）。

可选：批量检查多个分支（示例）：

```bash
for b in feature/a feature/b feature/c; do
  printf "%s: " "$b"
  if git merge-base --is-ancestor "origin/$b" origin/test; then
    echo "OK（已进 test，可合并到 release）"
  else
    echo "禁止：最新代码未进 test，请先合并到 test 后再合并到 release"
  fi
done
```

若任一分支未通过门禁，**不要**将该分支合并进 `release`；仅合并通过门禁的分支。

### 3. 合并到 `release`（本地或 PR/MR）

**方式 A：本地合并（团队允许时）**

```bash
git checkout release
git pull origin release

for b in feature/one feature/two; do
  # 每个分支合并前再次确认门禁（防止 fetch 后状态变化）
  git merge-base --is-ancestor "origin/$b" origin/test || { echo "跳过 $b：未进 test"; continue; }
  git merge "origin/$b" -m "merge $b into release"
done

git push origin release
```

**方式 B：PR/MR（推荐）**

- 对每个通过门禁的分支，在平台上创建 **Source: `feature/<name>` → Target: `release`** 的合并请求。
- 合并前在描述中注明已通过「相对 `origin/test` 的祖先校验」。

### 4. 合并后的分支清理（可选）

与 `git-merge-feature` 技能一致：可删除已完全合入的本地/远端功能分支（按团队规范）。

---

## 二、正式发版：release → main + 标签

在 `release` 上测试通过后，将 `release` 合入 `main` 并打正式版本标签。

### 1. 确保 `release` 最新

```bash
git checkout release
git pull origin release
```

### 2. 合并到 `main`（建议通过 PR/MR）

```bash
git checkout main
git pull origin main
git merge release
```

### 3. 在 `main` 上打 annotated 标签并推送

```bash
git tag -a v<version> -m "release v<version>"
git push origin main
git push origin v<version>
```

示例：

```bash
git tag -a v1.2.0 -m "release v1.2.0"
git push origin v1.2.0
```

---

## 版本号规则

| 类型 | 适用 | 示例 |
|------|------|------|
| **Patch** | 缺陷与小修正 | v1.0.0 → v1.0.1 |
| **Minor** | 新功能、兼容扩展 | v1.0.0 → v1.1.0 |
| **Major** | 破坏性变更 | v1.0.0 → v2.0.0 |

---

## 预发布标签（可选）

在 `release` 上可打 beta/rc 供预发验证；**正式标签必须在 `main` 上**。

```bash
git tag -a v1.2.0-beta.1 -m "beta v1.2.0-beta.1"
git tag -a v1.2.0-rc.1 -m "release candidate v1.2.0-rc.1"
```

---

## 执行本技能时的检查清单

| 步骤 | 说明 |
|------|------|
| 多选分支 | 列出用户要合并到 `release` 的所有 `feature/*` |
| TB 号校验 | 每个分支名必须符合 `feature/TB号-描述` 格式 |
| 逐个门禁 | 对每个分支执行 `git merge-base --is-ancestor origin/feature/<name> origin/test` |
| 阻断 | 任一失败则明确提示：**该分支最新代码未进 test，不能合并到 release**，并说明需先合入 `test` |
| 合并 | 仅对通过门禁的分支执行合并或指导创建 PR |
| 发版 | 需要正式发布时再走「二、正式发版」 |

## TB 号关联规范

### 合并 commit 关联 TB 号

合并功能分支时，commit message 应关联 TB 号：

```bash
git merge "origin/feature/TB1234-user-login" -m "merge feature/TB1234-user-login into release

Refs #TB1234"
```

### 发版标签关联

正式发版标签应包含本次发版涉及的 TB 号：

```bash
git tag -a v1.2.0 -m "release v1.2.0

Includes: TB1234, TB1235, TB1236"
```

---

## 要求摘要

- **test 门禁**：`origin/feature/<name>` 必须是 `origin/test` 的祖先，才允许进 `release`（见上文 `merge-base --is-ancestor`）。
- 正式标签使用 **annotated**（`-a`），语义化版本：`v<major>.<minor>.<patch>`。
- `release` → `main` 建议使用 PR/MR。
- 若仓库中预发分支不叫 `test` 而叫 `staging` 等，将命令中的 `test` 替换为实际分支名，但门禁逻辑不变。

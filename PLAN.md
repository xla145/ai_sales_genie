# Hermes workspace artifact preservation and prototype versioning plan

> SCOPE LOCK: 只规划“第二阶段开始产物保留到 Hermes agent 工作空间、项目相对路径一致、原型修改 v2/v3 版本复制”。未获批准前不继续改实现代码。

## Research Summary

### 用户要求
- 从第二阶段开始，所有生成文件都要在 Hermes agent 对应的工作空间保留一份。
- Hermes 工作空间中的保存路径需要与项目空间的相对地址一致，方便后续定位并修改对应原型设计。
- 修改原型返回后，项目空间需要保留上一版，再复制一份修改后的结果形成新版本。
- 每修改一次递增一个版本：首次原型生成是 `v1`，第一次修改为 `v2`，下一次修改为 `v3`。

### 当前相关实现分成两条路径
- `agent_runner_test/` 是已有 Hermes runner/产物/版本化试验路径，已经包含更接近目标的实现：
  - `agent_runner_test/agent_runner/storage/local_storage.py` 创建 `deliverables/current`、`deliverables/prototypes/vN`、`runs/`。
  - `agent_runner_test/agent_runner/worker/runner.py` 将 Hermes JSON 返回的 `files[]` 写入工作空间或原型版本目录。
  - `agent_runner_test/agent_runner/api/runs.py` 提供 `/runs/{run_id}/artifacts` 与下载接口。
- `app/` 是当前 FastAPI 主应用路径，生成文件主要保存在 session workspace：
  - `app/services/session_service.py` 创建 `data/projects/{project_id}/sessions/{session_id}`。
  - `app/runtime_core/tools/workspace.py` 的 `write_file` 直接写入 session workspace。
  - `app/services/hermes_runner.py` skill 路径会收集 expected outputs，非 skill 路径会 materialize JSON 返回。
  - 当前主应用没有显式的 prototype v1/v2/v3 版本目录，也没有 artifact 下载模型。

### `agent_runner_test` 当前未提交变更已覆盖的能力
- `agent_runner_test/run_prototype_flow.py` 已把 phase2 指令从“只输出两个最终文档”改为完整输出：
  - `系统全局功能描述与设计.md`
  - `系统的功能点设计.md`
  - `页面详细设计/页面名称.md`
  - `第二阶段设计检查报告.md`
- `agent_runner_test/agent_runner/worker/runner.py` 已新增阶段感知规则：
  - `phase2_design` 要求按中文原名/项目相对路径保留完整第二阶段文件。
  - `phase3_prototype` 要求 `prototype/` 路径写入当前原型版本目录。
  - `prototype_edit` 要求只返回变更 `prototype/` 文件，runner 保留上一版并生成新版本。
- `agent_runner_test/agent_runner/worker/runner.py` 已将允许路径扩展为：
  - `需求结构化.md`、`PRD.md`、`系统全局功能描述与设计.md`、`系统的功能点设计.md`、`第二阶段设计检查报告.md`
  - `页面详细设计/`
  - `generation-report.md`、`validation-report.md`
  - `prototype/`
- `agent_runner_test/agent_runner/storage/local_storage.py` 已支持旧 `project_root/current` 到新 `deliverables/current` 的一次性迁移，并记录 `copied_from_previous_version`。
- `agent_runner_test/agent_runner/api/runs.py` 已将 `run_type` 传入 runner，避免只靠 prompt/run_id 猜测阶段。
- `agent_runner_test/agent_runner/worker/runner.py` 已把 materialized files 也登记为 artifact，metadata 含 `project_relative_path` 与 `prototype_version`。

### 仍需重点确认的问题
- 当前 `agent_runner_test/agent_runner/worker/runner.py` 的 `LEGACY_DOCUMENT_PATHS` 会把英文旧路径映射到中文路径；第二阶段及之后符合“项目相对路径一致”，但若旧前端仍期待英文 `feature-points.md`，需要确认是否还要兼容读取。
- `prototype/...` 返回路径会被映射到 `deliverables/prototypes/vN/{...}`，即版本目录内不再包含外层 `prototype/` 目录；返回给调用方的 `path` 仍是 `prototype/...`。这与既有实现一致，需确认是否接受。
- `app/` 主应用目前没有同等的 prototype version store。如果用户实际使用的是主应用 workflow，而不是 `agent_runner_test` runner，则需要把版本化能力迁移到 `app/`。
- `app/services/hermes_runner.py` 与 `app/services/orchestrator_service.py` 对 `prototype/pages/*.html` 按字面路径校验，不支持 glob；如果启用主应用 phase3，可能误报未生成。
- `app/runtime_core/skills/executor.py` 只直接读取文件输入，目录输入如 `页面详细设计/` 需要 skill 通过 workspace tools 自行 list/read；当前 phase3 有 summary，但不自动展开全文。

### 数据流梳理：`agent_runner_test`
1. `run_prototype_flow.py` 创建 run，run_type 为 `phase2_design` / `phase3_prototype` / `prototype_edit`。
2. `api/runs.py::execute_run()` 查询 run 并调用 `Runner.run_once(..., run_type=run.get("run_type"))`。
3. `Runner.run_once()` 调用 `LocalStorage.build_project_paths(project_id)`，项目工作空间为 `deliverables/current`。
4. 对 `phase3_prototype` / `prototype_edit` 调用 `create_next_prototype_version()`：
   - 无当前版本时创建 `v1`。
   - 有当前版本时复制上一版目录到新 `vN`，再应用变更。
5. `_build_workspace_context()` 拼接 `deliverables/current` 文件内容；如果是原型 run，也把当前版本目录按 `prototype/...` 形式加入上下文。
6. Hermes 返回 JSON：`{"files":[{"path":"相对路径","content":"完整文件内容"}],"deleted_files":[...]}`。
7. `_materialize_response_files()`：
   - 非 `prototype/` 文件写入 `deliverables/current/{relative_path}`。
   - `prototype/...` 文件写入 `deliverables/prototypes/vN/{path_without_prototype_prefix}`。
   - 返回 `written_files`，其中 `path` 保留项目相对路径。
8. runner 保存 `hermes_output.md`、`patch.diff`、`manifest.json`，并为每个 materialized file 创建 artifact。
9. 成功后 `finalize_prototype_version()` 更新 `current_version.json` 的 `current_prototype_version`。

### 数据流梳理：`app/` 主应用
1. `app/services/orchestrator_service.py` 串行执行 phase1/phase2/phase3，每个阶段可拆 subtask。
2. `app/services/hermes_runner.py::execute_prompt_task()` 调用 `execute_skill()`。
3. skill 执行时通过 `app/runtime_core/tools/workspace.py` 的 `write_file` 写入 `session.workspace_path`。
4. skill 完成后 `_collect_workspace_files()` 从 session workspace 收集 expected outputs。
5. 当前没有将第二阶段/第三阶段产物复制到独立 Hermes deliverables workspace，也没有 `vN` 原型版本目录。

---

## Implementation Plan

### Decision: 先补齐并验证 `agent_runner_test` runner 路径
用户表述中的 “Hermes agent 对应工作空间” 与 `agent_runner_test` 中的 runner/workspace/artifact/version 机制最匹配；当前未提交 diff 已集中在这条路径。本轮计划先完成并验证这条路径，不迁移主应用 `app/` 架构，除非你确认实际入口是主应用 workflow。

### Constraints
- 第二阶段及之后不得丢弃 `页面详细设计/` 与 `第二阶段设计检查报告.md`。
- 第二阶段及之后返回路径和落盘路径必须保持项目相对路径语义；中文文件名不再强制改为英文别名。
- 原型版本不得覆盖上一版；每次 `prototype_edit` 必须复制上一版后写入新版本。
- `phase2_design` 不创建 prototype version。
- `phase3_prototype` 创建 `v1`；后续 `prototype_edit` 创建 `v2`、`v3`。
- 路径安全仍需拒绝绝对路径和 workspace 逃逸。

### Step 1: 校准阶段指令
- **File**: `agent_runner_test/run_prototype_flow.py`
- **Action**: 保留当前已改的 phase2/phase3/prototype_edit 指令，并检查措辞是否明确：
  - phase2 返回完整四类第二阶段产物。
  - phase3 基于完整第二阶段产物生成 `prototype/`。
  - prototype_edit 只返回需要变更的 `prototype/` 文件，runner 复制上一版。
- **Validation**: 静态检查 PHASES 中 `run_type` 与 runner 规则完全匹配。
- [ ] pending

### Step 2: 校准 allowed paths 与 path mapping
- **File**: `agent_runner_test/agent_runner/worker/runner.py`
- **Action**:
  - 保留 `ALLOWED_WORKSPACE_FILES` / `ALLOWED_WORKSPACE_PREFIXES`。
  - 确认 `系统全局功能描述与设计.md`、`页面详细设计/...`、`第二阶段设计检查报告.md` 不会被过滤。
  - 确认 `prototype/...` 仅在 prototype run 中允许写入版本目录。
  - 确认第二阶段中文路径不会被映射成 `feature-points.md`。
- **Validation**: 用单元级 Python 片段调用 `_materialize_response_files()` 写入临时 workspace，检查实际路径。
- [ ] pending

### Step 3: 校准 prototype version lifecycle
- **Files**:
  - `agent_runner_test/agent_runner/storage/local_storage.py`
  - `agent_runner_test/agent_runner/worker/runner.py`
- **Action**:
  - 保留 `create_next_prototype_version()` 复制上一版目录的行为。
  - 确认 `run_type in {"phase3_prototype", "prototype_edit"}` 是唯一版本触发条件。
  - 确认 `finalize_prototype_version()` 只在 runner 成功后调用。
- **Validation**: 用临时 project_id 调用 storage：创建 v1，写一个文件，finalize，再创建 v2，检查 v2 已复制 v1 且 `current_prototype_version` 未提前覆盖。
- [ ] pending

### Step 4: 校准 artifact 与 manifest
- **File**: `agent_runner_test/agent_runner/worker/runner.py`
- **Action**:
  - 保留 materialized file artifact 注册。
  - 确认 `manifest.json` 包含：
    - `workspace_path`
    - `legacy_workspace_path`
    - `project_relative_files`
    - `prototype_version`
    - `base_version`
    - `version_storage_path`
    - `copied_from_previous_version`
    - `written_files`
    - `deleted_files`
  - 确认 artifact metadata 含 `project_relative_path` 与 `prototype_version`。
- **Validation**: 静态检查返回结构，必要时用 mock DB/服务难度较大则先不做集成执行。
- [ ] pending

### Step 5: 加最小化自动测试或脚本级验证
- **Preferred**: 新增或运行已有轻量测试，覆盖 pure filesystem behavior：
  - 第二阶段路径 materialize。
  - prototype v1/v2 copy。
  - 绝对路径拒绝。
- **If no test harness exists**: 用 `python - <<'PY' ... PY` 临时脚本验证，不写入仓库测试文件。
- [ ] pending

### Step 6: 如实际入口是 `app/` 主应用，再做迁移计划
仅在你确认当前产品使用 `app/` 的 workflow 运行阶段二/三时执行，范围包括：
- 为 `app/` 增加 project-level deliverables/prototype version store。
- 让 `app/runtime_core/tools/workspace.py` 或 `app/services/hermes_runner.py` 从 phase2 开始同步写入 project deliverables。
- 让 phase3/prototype edit 写入 `prototypes/vN` 并保留上一版。
- 修复 `prototype/pages/*.html` glob 校验。
- 暴露 artifact/version 查询或下载 API。
- [ ] pending / optional

### Files expected to modify if approved
| File | Purpose |
| --- | --- |
| `agent_runner_test/run_prototype_flow.py` | 校准 phase2/phase3/prototype_edit 指令 |
| `agent_runner_test/agent_runner/worker/runner.py` | 路径允许、阶段规则、版本触发、manifest/artifact |
| `agent_runner_test/agent_runner/storage/local_storage.py` | current 兼容迁移、prototype version 复制元数据 |
| `agent_runner_test/agent_runner/api/runs.py` | 传递 run_type 到 runner |

### What will not change in this pass
- 不改数据库 schema。
- 不迁移主应用 `app/` 的架构，除非你确认它才是实际入口。
- 不覆盖旧版本原型。
- 不引入外部存储或新队列。

### Open Questions
1. 这次需求要落在 `agent_runner_test` runner，还是要迁移到主应用 `app/` 的 workflow/session workspace？
2. 版本目录内部是否接受当前设计：返回路径显示 `prototype/index.html`，实际存储为 `deliverables/prototypes/v1/index.html`；还是必须存为 `deliverables/prototypes/v1/prototype/index.html`？
3. 第二阶段是否还需要同时生成兼容旧读取逻辑的英文别名文件（如 `feature-points.md`），还是只保留中文项目相对路径？

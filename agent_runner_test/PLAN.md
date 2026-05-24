> SCOPE LOCK: 只设计 Hermes 工作空间产物保留、第二阶段完整产物保存、原型修改版本递增复制；未批准前不改实现代码。

## Research Summary

### 用户新要求
- 从第二阶段开始，所有生成的文件都要在 Hermes agent 对应的工作空间保留一份。
- Hermes 工作空间内的文件路径必须与项目空间的相对地址一致，方便后续修改对应原型设计。
- 最终把修改后的返回文件写回时，项目空间需要保留上一份版本。
- 每次原型修改时，再复制一份修改后的返回文件，生成递增版本：首次修改为 `v2`，下一次为 `v3`，以此类推。

### 当前调用入口与阶段指令
- `agent_runner_test/run_prototype_flow.py`
  - `PHASES` 定义了 `phase1`、`phase2`、`phase3` 三阶段。
  - 当前 `phase2` 指令只要求输出：
    - `系统全局功能描述与设计.md`
    - `系统的功能点设计.md`
  - 当前 `phase2` 指令明确要求不要输出：
    - `页面详细设计/`
    - `第二阶段设计检查报告.md`
  - 这与 orchestrator 与第二阶段 skill 的完整产物要求冲突，也无法满足后续原型生成需要页面详细设计的要求。
  - 当前 `phase3` 指令只要求输出 `prototype/`，并明确不要输出 `generation-report`、`validation-report` 等中间产物。
  - `--modify-prototype` 当前会创建一个 `prototype_edit` run，指令要求“修改当前原型并生成一个新的完整原型版本”，但让 Hermes “只返回需要变更的 `prototype/` 文件”。

### 当前服务端 Hermes 工作空间逻辑
- `agent_runner_test/agent_runner/worker/runner.py`
  - `Runner.run_once()` 调用 `LocalStorage.build_project_paths(project_id)`，当前工作空间为 `paths["current"]`。
  - 当前代码中的 `paths["current"]` 来自 `deliverables/current`。
  - 旧测试数据里存在 `data/projects/proj_rawreq_005/current/需求结构化.md`，但当前代码已改为 `data/projects/{project_id}/deliverables/current`，导致老数据与新代码路径不一致。
  - `_build_workspace_prompt()` 会把当前 workspace 文件内容拼入 prompt，并要求 Hermes 最终返回 JSON：
    - `{"files":[{"path":"相对路径","content":"完整文件内容"}],"deleted_files":["相对路径"]}`
  - 当前 prompt 明确写了：只保存最终产物：需求结构化、PRD、功能点、原型；不要返回页面详细设计、检查报告、临时分析等中间产物。
  - 这与新要求“从第二阶段开始所有生成文件都保留一份”冲突。

### 当前文件过滤与路径映射
- `agent_runner_test/agent_runner/worker/runner.py`
  - `FINAL_DOCUMENT_PATHS` 当前只允许/映射：
    - `需求结构化.md` → `requirements.md`
    - `PRD.md` / `prd.md` → `prd.md`
    - `系统的功能点设计.md` / `feature-points.md` → `feature-points.md`
    - `prototype/` 下文件
  - `_is_final_document_path()` 只接受 `FINAL_DOCUMENT_PATHS` 内路径或 `prototype/` 前缀。
  - `_materialize_response_files()` 会过滤掉不符合 `_is_final_document_path()` 的文件。
  - 因此即使 Hermes 返回：
    - `系统全局功能描述与设计.md`
    - `页面详细设计/xxx.md`
    - `第二阶段设计检查报告.md`
    当前也可能被过滤、改名或无法完整按原相对路径保留。
  - 当前 `系统全局功能描述与设计.md` 不在 `FINAL_DOCUMENT_PATHS` 中，存在被过滤风险。
  - 当前 `页面详细设计/` 与 `第二阶段设计检查报告.md` 会被过滤。

### 当前原型版本逻辑
- `agent_runner_test/agent_runner/storage/local_storage.py`
  - `create_next_prototype_version()` 使用 `deliverables/prototypes/vN` 保存原型版本。
  - `next_number = len(versions) + 1`，首次原型 run 会得到 `v1`。
  - 如果已有 `current_prototype_version`，会把上一版本目录复制到新版本目录，再写入本次变更。
  - `finalize_prototype_version()` 成功后把 `current_prototype_version` 更新为当前版本。
- `agent_runner_test/agent_runner/worker/runner.py`
  - `is_prototype_run = "prototype" in run_id or "原型" in prompt or "prototype" in prompt.lower()`。
  - 只要判断为原型 run，就会创建下一版 prototype 目录。
  - `_target_for_output_path()` 会把返回的 `prototype/...` 映射到当前版本目录 `deliverables/prototypes/vN/...`。
  - 这已经具备“基于上一版本复制再写变更”的基础能力。
  - 但当前 `--modify-prototype` 指令只返回变更文件，返回结果本身不会自动包含完整版本文件列表；完整版本存在于 `deliverables/prototypes/vN` 中。

### 当前 artifact 与返回下载逻辑
- `agent_runner_test/agent_runner/worker/runner.py`
  - 每次 run 会在 `data/projects/{project_id}/runs/{run_id}/` 保存：
    - `hermes_output.md`
    - `patch.diff`
    - `manifest.json`
  - artifacts 表只登记这三个 run 级 artifact。
  - `generated_files` 返回 `_materialize_response_files()` 实际写入的文件列表。
- `agent_runner_test/agent_runner/api/runs.py`
  - `/runs/{run_id}/artifacts` 返回 run 级 artifact 下载地址。
  - `/runs/{run_id}/artifacts/{artifact_id}` 只能下载已入库的 artifact 文件。
  - 当前没有把每个 materialized 文件逐个作为 artifact 入库，因此前端/调用方如果只依赖 artifact 下载接口，拿不到每个产物文件的下载项。

### 当前 project-relative 与 Hermes workspace-relative 的问题
- 当前 materialize 后的 `storage_path` 是绝对路径，但 `path` 是映射后的相对路径。
- 当前会把中文产物名映射为英文名，例如 `系统的功能点设计.md` → `feature-points.md`。
- 用户新要求是“跟项目的相对地址一致”，因此从第二阶段开始不应再把这些产物改名为英文路径；应保留 Hermes 返回路径与项目空间路径一致。
- 第一阶段是否继续映射 `需求结构化.md` → `requirements.md` 需要确认；本次用户明确说“从第二阶段开始”，因此计划只调整第二阶段及之后，尽量不破坏第一阶段既有行为。

### 关键冲突
1. 第二阶段 orchestrator/skill 要求四类产物，但 `run_prototype_flow.py` 当前只要求两个文件，并禁止页面详细设计和检查报告。
2. Runner prompt 当前要求不要返回页面详细设计、检查报告，与新要求冲突。
3. Runner 文件过滤当前不允许第二阶段完整产物落盘。
4. 当前原型版本从首次原型生成开始为 `v1`，修改后为 `v2` 的目标基本可满足；但需要明确只在 `prototype_edit`/原型阶段创建新版本，避免第二阶段误触发版本。
5. 当前旧测试数据使用 `data/projects/{project_id}/current`，当前代码使用 `data/projects/{project_id}/deliverables/current`，需要统一，避免阶段二找不到阶段一产物。

---

## Implementation Plan

### Overview
调整 runner 的阶段感知、文件保留策略和原型版本策略：第二阶段开始允许并要求完整产物按原相对路径写入 `deliverables/current`；原型文件继续进入 `deliverables/prototypes/vN`，每次原型修改先复制上一版本再应用返回文件，保持 `v1 → v2 → v3` 递增；run manifest 记录 project workspace 与 prototype version 的完整映射。

### Constraints (DO NOT VIOLATE)
- 不再丢弃第二阶段产物：`系统全局功能描述与设计.md`、`系统的功能点设计.md`、`页面详细设计/`、`第二阶段设计检查报告.md` 必须允许落盘。
- 第二阶段及之后保留项目相对路径，不把中文文件名强制改为英文别名。
- 原型修改必须保留上一版本目录，不覆盖旧版本。
- 每次原型修改都基于当前版本复制新版本，再写入 Hermes 返回的变更文件。
- 未批准前不改实现代码。

### Step 1: 调整阶段二/阶段三指令
- **File**: `agent_runner_test/run_prototype_flow.py`
- **Change**:
  - `phase2` instruction 改为要求完整输出四类第二阶段产物：
    - `系统全局功能描述与设计.md`
    - `系统的功能点设计.md`
    - `页面详细设计/页面名称.md`
    - `第二阶段设计检查报告.md`
  - 删除“不要输出页面详细设计、第二阶段设计检查报告”的限制。
  - `phase3` instruction 改为基于完整第二阶段产物生成完整 `prototype/`，并可按需要输出 `generation-report.md`、`validation-report.md`。
- **Sketch**:
  - phase2 prompt 明确：最终 JSON 的 files[].path 必须使用上述项目相对路径。
- [x] completed

### Step 2: 让 runner prompt 支持第二阶段完整产物
- **File**: `agent_runner_test/agent_runner/worker/runner.py`
- **Change**:
  - `_build_workspace_prompt()` 增加 run context 或 phase/run_type 信息，避免所有阶段共用“只保存最终产物”的限制。
  - 从第二阶段开始删除“不要返回页面详细设计、检查报告”的限制。
  - 明确要求：从第二阶段开始，所有生成文件必须返回完整 JSON 文件内容，并按项目相对路径保存。
  - 对 prototype edit 保持“可只返回变更文件”，runner 负责复制上一版本形成完整 vN。
- **Sketch**:
  - `artifact_policy = self._build_artifact_policy(run_type, prompt)`
  - phase2 policy: allow all design outputs.
  - prototype policy: return prototype paths only; runner versions them.
- [x] completed

### Step 3: 调整文件允许规则，保留第二阶段路径
- **File**: `agent_runner_test/agent_runner/worker/runner.py`
- **Change**:
  - 替换或扩展 `FINAL_DOCUMENT_PATHS`，使第二阶段及之后允许：
    - `系统全局功能描述与设计.md`
    - `系统的功能点设计.md`
    - `页面详细设计/...`
    - `第二阶段设计检查报告.md`
    - `generation-report.md`
    - `validation-report.md`
    - `prototype/...`
  - 第二阶段及之后不再把 `系统的功能点设计.md` 映射为 `feature-points.md`。
  - 保留第一阶段 `需求结构化.md` 的兼容策略，或者增加同时兼容中文原名和旧英文名。
- **Sketch**:
  - `ALLOWED_WORKSPACE_PREFIXES = ("页面详细设计/",)`
  - `ALLOWED_WORKSPACE_FILES = {...}`
  - `_target_for_output_path()` 默认使用原始 relative path，仅对 prototype 做版本目录映射。
- [x] completed

### Step 4: 统一项目工作空间 current 路径兼容
- **File**: `agent_runner_test/agent_runner/storage/local_storage.py`, `agent_runner_test/agent_runner/worker/runner.py`
- **Change**:
  - 继续以 `deliverables/current` 作为新标准项目空间。
  - 在必要时为旧路径 `data/projects/{project_id}/current` 做一次性兼容迁移/读取：如果 `deliverables/current` 为空且旧 `current` 存在，则复制旧 `current` 到 `deliverables/current`。
  - 避免阶段二因第一阶段旧产物在旧目录而失败。
- **Sketch**:
  - `ensure_current_workspace(project_id)` copies legacy files only when new workspace has no files.
- [x] completed

### Step 5: 收紧原型版本触发规则
- **File**: `agent_runner_test/agent_runner/worker/runner.py`, possibly `agent_runner_test/agent_runner/api/runs.py`
- **Change**:
  - 优先根据 `run_type` 判断是否为原型生成/修改，而不是只靠 run_id/prompt 字符串。
  - `phase3_prototype` 生成 `v1`。
  - `prototype_edit` 基于当前版本复制生成 `v2`、`v3` 等。
  - 第二阶段 run 不创建 prototype 版本。
- **Sketch**:
  - pass `run_type` into `runner.run_once(...)` from `execute_run()`.
  - `is_prototype_run = run_type in {"phase3_prototype", "prototype_edit"}`.
- [x] completed

### Step 6: manifest 记录完整映射与版本信息
- **File**: `agent_runner_test/agent_runner/worker/runner.py`
- **Change**:
  - `manifest.json` 增加：
    - `workspace_path`
    - `project_relative_files`
    - `prototype_version`
    - `base_version`
    - `version_storage_path`
    - `copied_from_previous_version`
  - 用于后续定位“项目空间保留哪一份，v2/v3 修改结果在哪里”。
- **Sketch**:
  - `manifest["written_files"]` 继续保留 `path` 与 `storage_path`。
- [x] completed

### Step 7: 把 materialized 文件登记为 artifacts
- **File**: `agent_runner_test/agent_runner/worker/runner.py`, `agent_runner_test/agent_runner/services/artifact_service.py`
- **Change**:
  - 除 `hermes_output.md`、`patch.diff`、`manifest.json` 外，把每个写入的产物文件也保存 artifact 记录。
  - artifact metadata 记录 `project_relative_path`、`prototype_version`。
  - 这样后续页面可以直接通过 artifacts 列表展示 PRD、功能点列表、页面设计文件、原型文件。
- [x] completed

### Step 8: 为功能点列表生成结构化 JSON
- **File**: `agent_runner_test/run_prototype_flow.py`, `agent_runner_test/agent_runner/worker/runner.py`
- **Change**:
  - phase2 指令在保留 `系统的功能点设计.md` 的同时，额外要求输出 `系统的功能点设计.json`。
  - JSON 用于后续表格展示，至少包含功能点列表数组与每项的名称、模块、说明、优先级/状态等可展示字段。
  - runner 的 allowed paths 增加 `系统的功能点设计.json`，并作为 materialized artifact 登记。
  - PRD 展示仍读取 `系统全局功能描述与设计.md`，不新增 `PRD.md` 要求。
- [x] completed

### Step 9: 验证场景
- **Commands**:
  - 运行阶段二：确认 `deliverables/current/系统全局功能描述与设计.md`、`deliverables/current/系统的功能点设计.md`、`deliverables/current/系统的功能点设计.json`、`deliverables/current/页面详细设计/*.md`、`deliverables/current/第二阶段设计检查报告.md` 存在。
  - 运行阶段三：确认 `deliverables/prototypes/v1/prototype/...` 或版本目录中的原型文件存在，且 `current_version.json` 指向 `v1`。
  - 运行一次 `--modify-prototype`：确认 `v2` 从 `v1` 复制而来，变更文件写入 `v2`，`v1` 保留。
  - 再运行一次 `--modify-prototype`：确认生成 `v3`，`v2` 保留。
- [x] completed

### Files to modify
| File | Change | Why |
|------|--------|-----|
| `agent_runner_test/run_prototype_flow.py` | 调整阶段二/三与原型修改指令 | 让 Hermes 返回完整阶段产物 |
| `agent_runner_test/agent_runner/worker/runner.py` | 阶段感知 prompt、允许路径、功能点 JSON、版本触发、manifest | 实现产物保留与版本化核心逻辑 |
| `agent_runner_test/agent_runner/storage/local_storage.py` | current 路径兼容、版本复制元数据 | 避免旧 workspace 断裂，增强版本记录 |
| `agent_runner_test/agent_runner/api/runs.py` | 将 run_type 传给 runner | 避免靠 prompt/run_id 猜测阶段 |
| `agent_runner_test/agent_runner/services/artifact_service.py` | 如需批量登记产物 artifact | 支撑后续页面展示产物列表 |

### What will NOT change
- 不改数据库 schema，除非实现时发现 artifact metadata 无法满足需求。
- 不引入新的队列、鉴权或外部存储。
- 不把旧版本原型覆盖为最新版本。

### Decisions from annotations
1. PRD 页面展示数据源使用 `系统全局功能描述与设计.md`，不要求 Hermes 额外生成标准 `PRD.md`。
2. 功能点列表需要结构化 JSON，因为后续要用于表格展示；不能只依赖 `系统的功能点设计.md` 文本读取。
3. 原型版本目录沿用当前映射：返回路径仍显示为 `prototype/...`，实际存储在 `deliverables/prototypes/vN/...`，不额外嵌套 `prototype/` 目录。

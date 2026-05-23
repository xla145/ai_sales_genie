> SCOPE LOCK: 在 agent_runner_test 中按顺序落地 Alembic 初始化、MySQL CRUD、SSE 增量事件流、Hermes 调用与 patch 入库，不扩展额外能力。

## Research Summary
- `agent_runner/main.py` — FastAPI 入口，仅注册 `/projects`、`/runs`、`/events` 路由和健康检查。
- `agent_runner/api/projects.py` — 目前仅回显 payload，没有数据库写入。
- `agent_runner/api/runs.py` — 目前仅回显 payload，没有 run 状态流转。
- `agent_runner/api/events.py` — 仅返回空数组，尚未接入 run_events。
- `agent_runner/db/session.py` — 已有 AsyncEngine + AsyncSessionLocal + 依赖注入函数 `get_db_session`，可直接用于 CRUD。
- `agent_runner/db/models.py` — 已定义 `projects/project_sessions/project_runs/requirements/run_messages/run_events/tool_calls/file_changes/artifacts` 九张核心表模型，字段与 `doc/技术方案.md` 基本一致，可作为初始 migration 源。
- `agent_runner/services/*.py` — service 层均为占位回包，需要替换成真实 DB 逻辑。
- `agent_runner/storage/local_storage.py` — 已支持项目目录初始化，可用于 patch 文件落盘。
- `agent_runner/services/hermes_service.py` — 当前 mock 规划返回，需要替换为 HTTP 调用 Hermes。
- `agent_runner/worker/runner.py` — 当前仅返回 success，需要接入 Hermes + 事件 + artifact 入库流程。
- `requirements.txt` — 已包含 `alembic/sqlalchemy/aiomysql`，不需新增迁移基础依赖。
- Key finding: 当前代码是“骨架版”，数据库模型已就绪，最小闭环可通过“API → service → DB → 事件/SSE → runner”完成。
- Key finding: 现有模型无 FK 约束（除了索引），CRUD 逻辑需在应用层保证 `project_id/run_id/session_id` 一致性。

---

## Implementation Plan

### Overview
先建立 Alembic 基线，保证模型可迁移；再将项目/run/event 路由接入 MySQL；随后增加基于 `run_events.id` 的 SSE 增量流；最后在 runner 中调用 Hermes 并把 patch 写入本地存储与 artifacts 表，形成最小可追溯闭环。

### Constraints (DO NOT VIOLATE)
- `agent_runner/db/models.py` — 作为当前数据契约，不做破坏性字段删除或改名，避免迁移与业务逻辑错位。
- `/projects`、`/runs`、`/events` 路径 — 保持现有 API 前缀不变，避免调用方断裂。
- 仅实现最小闭环 — 不引入队列系统、鉴权、复杂任务编排。

### Steps

#### Step 1: 初始化 Alembic 与首个迁移
- **File**: `agent_runner_test/alembic.ini`, `agent_runner_test/alembic/env.py`, `agent_runner_test/alembic/versions/*.py`
- **Change**: 新增 Alembic 配置，接入 `agent_runner.db.base.Base.metadata`，创建初始建表迁移。
- **Sketch**: `target_metadata = Base.metadata`
- [x] done

#### Step 2: 落地 MySQL CRUD（projects/runs/events）
- **File**: `agent_runner/services/project_service.py`, `agent_runner/services/run_service.py`, `agent_runner/services/event_service.py`, `agent_runner/api/projects.py`, `agent_runner/api/runs.py`, `agent_runner/api/events.py`
- **Change**: 用 AsyncSession 实现创建项目、创建 run、写入/查询 run_events；API 注入 DB session 并调用 service。
- **Sketch**: `await session.execute(select(...).where(...))`
- [x] done

#### Step 3: 增加 SSE 增量事件流
- **File**: `agent_runner/api/events.py`, `agent_runner/services/event_service.py`
- **Change**: 新增 SSE endpoint，按 `after_id` 增量拉取 `run_events`，输出 `text/event-stream`。
- **Sketch**: `StreamingResponse(event_generator(), media_type="text/event-stream")`
- [x] done

#### Step 4: Hermes 调用与 patch 入库
- **File**: `agent_runner/services/hermes_service.py`, `agent_runner/worker/runner.py`, `agent_runner/services/artifact_service.py`, `agent_runner/storage/local_storage.py`（如需小幅补充）
- **Change**: Hermes HTTP 调用（超时/异常映射最小处理）、patch 落盘、artifacts 入库、run_events/tool_calls 记录、run 状态收敛。
- **Sketch**: `patch_text = await hermes.generate_patch(...)`
- [x] done

### Files to modify / create
| File | Change | Why |
|------|--------|-----|
| `agent_runner_test/PLAN.md` | create | 固化研究和执行范围 |
| `agent_runner_test/alembic.ini` | create | Alembic 主配置 |
| `agent_runner_test/alembic/env.py` | create | 连接模型 metadata |
| `agent_runner_test/alembic/script.py.mako` | create | Alembic 模板 |
| `agent_runner_test/alembic/versions/*.py` | create | 初始建表迁移 |
| `agent_runner/services/project_service.py` | modify | 项目 CRUD |
| `agent_runner/services/run_service.py` | modify | run CRUD 与状态更新 |
| `agent_runner/services/event_service.py` | modify | 事件写入/增量读取 |
| `agent_runner/services/artifact_service.py` | modify | artifact 入库 |
| `agent_runner/services/hermes_service.py` | modify | 调用 Hermes API |
| `agent_runner/api/projects.py` | modify | 路由接入 service+DB |
| `agent_runner/api/runs.py` | modify | 路由接入 service+DB |
| `agent_runner/api/events.py` | modify | 列表与 SSE |
| `agent_runner/worker/runner.py` | modify | Hermes + patch + 入库流程 |

### What will NOT change
- 不改动前端与主工程 `app/` 下代码。
- 不实现生产级任务队列、重试编排和权限体系。

### Risks / trade-offs
- 当前 `run_id/project_id` 由调用方传入，若重复会触发唯一键冲突；先保持简单失败返回。
- SSE 采用轮询读库实现，吞吐较低但足够支持最小测试闭环。
- Hermes 响应结构可能不稳定，先兼容常见 `patch`/`content` 字段。

---

## Deferred
- requirement 深度拆解写入（requirements 全链路）
- tool_calls 全量细粒度埋点
- 对象存储 S3 真正实现

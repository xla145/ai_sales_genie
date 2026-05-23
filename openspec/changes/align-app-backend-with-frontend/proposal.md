## Why

前端工作区页面（项目概览、需求录入、需求分析等）已定义完整的 TypeScript 数据契约与交互流程，但 app 后端仍将业务数据分散存储在 JSON 文件与 MySQL 头表之间：`SqlHeaderStore` 读取项目时 `config` 恒为空，概览字段与 `requirementAnalysis` 仅依赖文件系统。这导致前后端数据结构不一致、查询困难、并发写入风险高，也无法支撑后续情报/方案等页面的持久化扩展。需要以前端页面契约为准，补齐数据库表、实体类与接口/业务层设计。

## What Changes

- 新增项目概览与需求分析相关的 MySQL 表结构（DDL），与 `frontend/src/types/project.ts` 字段对齐。
- 新增 SQLAlchemy 实体类（`db_models.py`）及 Pydantic 领域模型，统一读写路径。
- 调整 `ProjectService` / `SqlHeaderStore`：概览与需求分析优先落库，文件 `project_config.json` 作为兼容层或逐步废弃。
- 保持现有 REST API 路径不变（`PATCH /overview`、`PATCH /requirement-analysis`、`POST /phase1/run`），响应体 `Project.config` 结构与前端一致。
- 补充 phase1 同步逻辑：AI 产出《需求结构化.md》解析后写入数据库表，而非仅写 JSON。
- **BREAKING（内部）**：启用 MySQL 后，项目 config 以数据库为准；需执行迁移脚本并回填已有 JSON 数据。

## Capabilities

### New Capabilities

- `project-overview-persistence`: 项目概览字段（clientInfo、province、city、stage、industry）的数据库持久化与 API 读写。
- `requirement-analysis-persistence`: 需求分析结构化数据（basic、core、scenarios、functions、risks、pending、attachments、supplement）的数据库表设计与 CRUD。
- `requirement-phase1-db-sync`: 第一阶段运行完成后，将《需求结构化.md》解析结果同步写入需求分析相关表。

### Modified Capabilities

- None.

## Impact

- 数据库：`sql/hermes_schema.sql` 新增表；需 migration/回填脚本
- 实体层：`app/storage/db_models.py`
- 模型层：`app/models/project.py`（类型细化，与前端对齐）
- 服务层：`app/services/project_service.py`、`app/storage/sql_header_store.py`
- API 层：`app/api/projects.py`（行为不变，数据源切换）
- 前端：无需改接口契约；`RequirementAnalysisView`、`RequirementInputView`、`ProjectOverviewView` 可直接消费
- 与现有变更 `complete-phase1-requirement-analysis` 的关系：字段映射规则可复用，本变更负责持久化层与整体后端结构调整

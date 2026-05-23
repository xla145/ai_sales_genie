## Context

前端以 `Project.config` 承载业务数据，其中：
- **概览字段**：`clientInfo`、`province`、`city`、`stage`、`industry`（`ProjectOverviewView`、`ProjectLayout`）
- **需求分析**：`requirementAnalysis` 含 8 个分区（`RequirementAnalysisView`、`RequirementInputView`），TypeScript 类型定义于 `frontend/src/types/project.ts`

后端现状：
- MySQL 仅存 `projects` / `project_sessions` / `project_runs` / `workflows` 头表（`sql/hermes_schema.sql`）
- `Project.config` 写入 `data/projects/{id}/project_config.json`（`app/storage/header_paths.py`）
- `SqlHeaderStore.get_project()` 返回 `config={}`，依赖 `ProjectService._hydrate_project_config()` 从文件补全
- phase1 解析逻辑已在 `ProjectService.build_requirement_analysis_from_phase1()` 实现，结果写 JSON

约束：FastAPI + SQLAlchemy + Pydantic；保持现有 API 路径；Docker Compose 已含 MySQL。

## Goals / Non-Goals

**Goals:**
- 以前端 `RequirementAnalysis` / `ProjectConfig` 为唯一契约，设计并落地 MySQL 表结构
- 新增 SQLAlchemy 实体，实现 config 的数据库读写
- `GET/PUT/PATCH` 项目相关接口返回的 `Project.config` 与前端类型一致
- phase1 完成后自动同步到数据库
- 提供 JSON → DB 回填脚本

**Non-Goals:**
- 不改前端页面与 API 路径
- 不实现真实文件上传/OSS（附件仍为 `{name, meta}` 记录）
- 不覆盖情报/方案/开发等尚未对接后端的页面（仅预留扩展位）
- 不重构 Hermes Runner / Workflow 引擎

## Decisions

### 1. 混合存储：标量列 + JSON 列 + 子表

| 数据 | 存储方式 | 理由 |
|------|----------|------|
| 项目概览 5 字段 | `projects` 表新增列 | 简单查询、列表展示 |
| basic / core 标量 | `requirement_analyses` 表列 | 与前端对象一一对应 |
| functions 三组字典 | `requirement_analyses` 三个 JSON 列 | 键名为中文标签，结构固定但适合 JSON |
| scenarios / risks / pending.items | 独立子表 | 列表 CRUD、排序、前端数组语义 |
| pending.unknownInfo / assumptions | `requirement_analyses` 列 | 长文本 |
| attachments | `project_attachments` 子表 | 列表增删 |
| supplement.notes | `requirement_analyses` 列 | 单字段 |

**Alternatives considered:**
- 整包 `config` 存单个 JSON 列：实现快但无法索引、列表项难维护
- 全部拆成关系表包括 functions：过度规范化，键名动态性低但维护成本高

### 2. 表结构设计

```sql
-- projects 表扩展
ALTER TABLE projects ADD COLUMN client_info VARCHAR(255) NULL;
ALTER TABLE projects ADD COLUMN province VARCHAR(64) NULL;
ALTER TABLE projects ADD COLUMN city VARCHAR(64) NULL;
ALTER TABLE projects ADD COLUMN stage VARCHAR(64) NULL;
ALTER TABLE projects ADD COLUMN industry VARCHAR(128) NULL;

-- 需求分析主表（1:1 project）
CREATE TABLE requirement_analyses (
    project_id VARCHAR(32) PRIMARY KEY,
    -- basic
    project_name VARCHAR(255) NOT NULL DEFAULT '',
    project_summary TEXT NOT NULL,
    basic_industry VARCHAR(128) NOT NULL DEFAULT '',
    project_type VARCHAR(128) NOT NULL DEFAULT '',
    keywords VARCHAR(512) NOT NULL DEFAULT '',
    -- core
    background TEXT NOT NULL,
    goal TEXT NOT NULL,
    users TEXT NOT NULL,
    pain_points TEXT NOT NULL,
    -- functions (JSON)
    function_desc JSON NOT NULL,
    non_function JSON NOT NULL,
    constraints_json JSON NOT NULL,
    -- pending scalar
    unknown_info TEXT NOT NULL,
    assumptions TEXT NOT NULL,
    -- supplement
    supplement_notes TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE TABLE requirement_scenarios (...);
CREATE TABLE requirement_risks (...);
CREATE TABLE requirement_pending_items (...);
CREATE TABLE project_attachments (...);
```

子表均含 `project_id`、`sort_order`（INT）、业务字段，按 `sort_order` 排序返回。

### 3. 实体与模型分层

```
app/storage/db_models.py     → SQLAlchemy ORM（RequirementAnalysisRecord 等）
app/models/project.py        → Pydantic API 契约（已有 RequirementAnalysisPatch 等，细化类型）
app/services/requirement_analysis_repository.py  → 新建：DB ↔ Pydantic 转换
app/services/project_service.py → 调用 repository，替代直接写 JSON
```

`ProjectService.get_project()` 组装流程：
1. `SqlHeaderStore` 读 `projects` 行（含概览列）
2. `RequirementAnalysisRepository.load(project_id)` 读主表 + 子表
3. 合并为 `Project.config` 字典返回

### 4. API 行为保持不变

| 端点 | 变更 |
|------|------|
| `GET /projects/{id}` | config 从 DB 组装 |
| `PATCH /projects/{id}/overview` | 写 projects 概览列 + 可选 name/description |
| `PATCH /projects/{id}/requirement-analysis` | 部分更新 requirement_analyses + 子表 |
| `POST /projects/{id}/phase1/run` | 运行后 `sync_requirement_analysis_from_phase1` 写 DB |

响应体 `Project` 结构不变，前端零改动。

### 5. phase1 同步策略

复用现有 `build_requirement_analysis_from_phase1()` 解析逻辑，输出 dict 后调用 `RequirementAnalysisRepository.save_full()` 全量替换子表（事务内 delete + insert）。

与 `complete-phase1-requirement-analysis` 变更：该变更管映射规则，本变更管落库；实现时可合并字段映射改进。

### 6. 文件 JSON 兼容策略

过渡期双写：`save_project()` 同时写 DB 与 `project_config.json`（便于回滚）。
读取以 DB 为准；若 DB 无记录则 fallback 读 JSON 并 lazy migrate。

## Risks / Trade-offs

- **[Risk] 双写不一致** → 以 DB 为 source of truth；JSON 仅备份；事务失败则不写 JSON
- **[Risk] 大文本性能** → TEXT 列足够；暂不做分页
- **[Risk] 迁移遗漏历史项目** → 提供 `scripts/migrate_config_to_db.py` 扫描 `data/projects/*/project_config.json`
- **[Risk] functions JSON 键名变更** → 以 `frontend/src/types/project.ts` 默认值为准，后端 `_create_default_requirement_analysis()` 保持一致

## Migration Plan

1. 执行 DDL（`sql/hermes_schema.sql` 追加或独立 migration 文件）
2. 部署新代码（双写模式）
3. 运行回填脚本处理存量项目
4. 验证前端需求录入 → phase1 → 需求分析页全链路
5. 观察稳定后可选关闭 JSON 双写

回滚：保留 JSON 文件；若 DB 故障可临时切回 `_hydrate_project_config()` 读文件。

## Open Questions

- 附件未来是否接入对象存储？当前仅 `{name, meta}` 记录，表结构已预留 `storage_path` 可空列。
- 情报/方案页面后续是否共用 `project_id` 下新表？本变更不阻塞，概览与需求分析独立成组。

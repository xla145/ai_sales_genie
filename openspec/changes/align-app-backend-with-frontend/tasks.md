## 1. 数据库表结构

- [x] 1.1 在 `sql/hermes_schema.sql` 扩展 `projects` 表：新增 `client_info`、`province`、`city`、`stage`、`industry` 列
- [x] 1.2 新增 `requirement_analyses` 主表（basic/core/functions JSON/pending 文本/supplement 列，1:1 关联 `projects`）
- [x] 1.3 新增 `requirement_scenarios` 子表（`project_id`、`sort_order`、`item_key`、`title`、`description`、`flow`）
- [x] 1.4 新增 `requirement_risks` 子表（`project_id`、`sort_order`、`item_key`、`title`、`level`、`description`、`impact`、`strategy`）
- [x] 1.5 新增 `requirement_pending_items` 子表（`project_id`、`sort_order`、`title`、`text`、`checked`）
- [x] 1.6 新增 `project_attachments` 子表（`project_id`、`sort_order`、`name`、`meta`，可选 `storage_path` 预留）
- [x] 1.7 编写独立 migration SQL 或 Alembic 脚本，支持在已有库上增量执行

## 2. SQLAlchemy 实体类

- [x] 2.1 在 `app/storage/db_models.py` 扩展 `ProjectRecord` 概览列
- [x] 2.2 新增 `RequirementAnalysisRecord` 实体及与 `ProjectRecord` 的 relationship
- [x] 2.3 新增 `RequirementScenarioRecord`、`RequirementRiskRecord`、`RequirementPendingItemRecord`、`ProjectAttachmentRecord` 实体
- [x] 2.4 配置级联删除（`ON DELETE CASCADE`）与子表 `sort_order` 索引

## 3. Pydantic 模型与转换层

- [x] 3.1 细化 `app/models/project.py`：将 `RequirementAnalysisPatch` 等类型的 `dict` 替换为与前端对齐的嵌套模型（可选保留 `dict` 兼容）
- [x] 3.2 新建 `app/services/requirement_analysis_repository.py`：实现 `load(project_id) -> dict` 与 `save_partial` / `save_full`
- [x] 3.3 实现 DB 行 ↔ `RequirementAnalysis` dict 双向转换（含 functions JSON 三组、子表排序）
- [x] 3.4 实现概览字段 camelCase ↔ snake_case 映射工具

## 4. 业务服务层调整

- [x] 4.1 调整 `ProjectService.create_project()`：创建项目时初始化空 `requirement_analyses` 记录
- [x] 4.2 调整 `ProjectService.get_project()` / `_hydrate_project_config()`：优先从 DB 组装 `config`，JSON 文件作 fallback
- [x] 4.3 调整 `ProjectService.update_project_overview()`：写 `projects` 概览列而非仅 JSON
- [x] 4.4 调整 `ProjectService.update_requirement_analysis()`：调用 repository 部分更新 DB
- [x] 4.5 调整 `ProjectService.sync_requirement_analysis_from_phase1()`：解析后 `save_full` 写 DB
- [x] 4.6 调整 `ProjectService.save_project()`：过渡期双写 DB + `project_config.json`
- [x] 4.7 调整 `SqlHeaderStore.get_project()` / `list_projects()`：读取概览列；config 由 service 层 hydrate

## 5. API 层验证

- [x] 5.1 确认 `app/api/projects.py` 现有端点无需改路径，手动验证响应体结构与 `frontend/src/types/project.ts` 一致
- [ ] 5.2 验证 `PATCH /overview`、`PATCH /requirement-analysis`、`POST /phase1/run` 端到端行为
- [x] 5.3 验证 `GET /projects` 列表接口返回的 config 不为空（至少含默认 requirementAnalysis）

## 6. 数据迁移与测试

- [x] 6.1 编写 `scripts/migrate_config_to_db.py`：扫描 `data/projects/*/project_config.json` 回填数据库
- [ ] 6.2 为 `RequirementAnalysisRepository` 添加单元测试（load/save_partial/save_full/子表替换）
- [ ] 6.3 为 `update_project_overview` 与 `sync_requirement_analysis_from_phase1` 添加集成测试
- [ ] 6.4 在 Docker Compose 环境执行 DDL + 迁移 + 前端需求录入→分析全链路冒烟

## 7. 文档同步

- [x] 7.1 更新 `sql/hermes_schema.sql` 注释说明各表与前端字段对应关系
- [ ] 7.2 在 `doc/技术方案v1.md` 或模块 design 中补充「项目 config 持久化」章节（表结构 + 读写流程）

## 8. 代码生成执行方式（fastapi-backend-codegen）

- [x] 8.1 实施阶段使用 `/Users/mac/xula/ai_sales_genie/.claude/skills/fastapi-backend-codegen` 技能生成 FastAPI 后端骨架与接口实现
- [x] 8.2 生成顺序遵循本 tasks 清单：先 DDL/实体，再 repository/service，再 API 对接
- [x] 8.3 每个生成批次后执行最小验证（导入检查、路由注册检查、关键接口联调）并修正类型/字段映射

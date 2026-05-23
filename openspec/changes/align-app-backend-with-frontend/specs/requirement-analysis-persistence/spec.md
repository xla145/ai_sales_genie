## ADDED Requirements

### Requirement: 需求分析结构化持久化

系统 SHALL 将前端 `RequirementAnalysis` 结构完整持久化到数据库，包括：`basic`、`core`、`functions`（三组 JSON）、`scenarios`、`risks`、`pending`（含 `items`）、`attachments`、`supplement`。

#### Scenario: 读取完整需求分析

- **WHEN** 客户端调用 `GET /projects/{project_id}` 且该项目已有需求分析数据
- **THEN** 响应体 `config.requirementAnalysis` SHALL 包含全部 8 个分区
- **AND** 各分区字段名与类型 SHALL 与 `frontend/src/types/project.ts` 中 `RequirementAnalysis` 一致

#### Scenario: 部分更新需求分析

- **WHEN** 客户端调用 `PATCH /projects/{project_id}/requirement-analysis` 仅提交 `basic.projectSummary`
- **THEN** 系统 SHALL 仅更新对应列/记录
- **AND** 其他已有字段 SHALL 保持不变

#### Scenario: 更新场景列表

- **WHEN** 客户端提交完整的 `scenarios` 数组（含新增、删除项）
- **THEN** 系统 SHALL 在事务内替换该项目的 `requirement_scenarios` 子表记录
- **AND** 返回的场景顺序 SHALL 与请求数组顺序一致

#### Scenario: 更新风险列表

- **WHEN** 客户端提交完整的 `risks` 数组
- **THEN** 系统 SHALL 在事务内替换 `requirement_risks` 子表记录
- **AND** 每项 SHALL 保留 `key`、`title`、`level`、`description`、`impact`、`strategy`

#### Scenario: 更新待确认清单

- **WHEN** 客户端提交 `pending.items` 数组及 `unknownInfo`、`assumptions`
- **THEN** 系统 SHALL 更新 `requirement_analyses` 中的文本列及 `requirement_pending_items` 子表
- **AND** `checked` 字段 SHALL 正确持久化

#### Scenario: 更新附件记录

- **WHEN** 客户端提交 `attachments` 数组（仅 name/meta，无文件二进制）
- **THEN** 系统 SHALL 在 `project_attachments` 表中存储记录
- **AND** 删除附件时 SHALL 移除对应行

#### Scenario: functions 三组字典持久化

- **WHEN** 客户端提交 `functions.functionDesc`、`functions.nonFunction`、`functions.constraints`
- **THEN** 系统 SHALL 将三组分别存入 `requirement_analyses` 的 JSON 列
- **AND** 读取时 SHALL 还原为与前端相同的嵌套对象结构

#### Scenario: 新建项目默认需求分析

- **WHEN** 客户端创建新项目且未提供 `config.requirementAnalysis`
- **THEN** 系统 SHALL 创建空的 `requirement_analyses` 主记录及默认子表占位（与 `_create_default_requirement_analysis()` 一致）

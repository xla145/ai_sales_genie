## ADDED Requirements

### Requirement: 项目概览字段持久化

系统 SHALL 在 `projects` 表中持久化项目概览字段：`client_info`、`province`、`city`、`stage`、`industry`，并与前端 `UpdateProjectOverviewRequest` 字段名（camelCase API / snake_case DB）一一映射。

#### Scenario: 更新项目概览

- **WHEN** 客户端调用 `PATCH /projects/{project_id}/overview` 并提交 `clientInfo`、`province`、`city`
- **THEN** 系统 SHALL 将对应值写入 `projects` 表
- **AND** `GET /projects/{project_id}` 返回的 `config.clientInfo`、`config.province`、`config.city` 与提交值一致

#### Scenario: 读取项目概览

- **WHEN** 客户端调用 `GET /projects/{project_id}`
- **THEN** 系统 SHALL 从 `projects` 表读取概览列并填入 `Project.config`
- **AND** 不得因启用 MySQL 而返回空 `config`

#### Scenario: 概览与 name/description 可同时更新

- **WHEN** 客户端在 overview 请求中同时提交 `name` 与 `industry`
- **THEN** 系统 SHALL 更新 `projects.name` 与 `projects.industry`
- **AND** 响应体 `Project.name` 与 `config.industry` 均反映最新值

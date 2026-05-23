## ADDED Requirements

### Requirement: Phase1 结果同步至数据库

系统 SHALL 在 `POST /projects/{project_id}/phase1/run` 成功完成后，将《需求结构化.md》解析结果写入需求分析相关数据库表，而非仅写入 JSON 文件。

#### Scenario: Phase1 运行成功后自动同步

- **WHEN** phase1 run 状态变为 success 且工作区存在 `需求结构化.md`
- **THEN** 系统 SHALL 调用解析逻辑生成 `requirementAnalysis` 结构
- **AND** SHALL 全量写入 `requirement_analyses` 及关联子表
- **AND** `RunPhase1Response.project.config.requirementAnalysis` SHALL 包含同步后的数据

#### Scenario: 同步保留用户已编辑字段的合理合并

- **WHEN** 项目中已有用户手动编辑的需求分析数据
- **AND** phase1 再次运行
- **THEN** 系统 SHALL 按现有 `build_requirement_analysis_from_phase1()` 合并策略：AI 解析结果优先填充空字段，已有非空字段按设计规则保留或覆盖
- **AND** 最终结果 SHALL 写入数据库

#### Scenario: 同步失败时不破坏已有数据

- **WHEN** phase1 run 失败或 `需求结构化.md` 不存在
- **THEN** 系统 SHALL NOT 清空已有需求分析数据库记录
- **AND** SHALL 返回相应错误状态

#### Scenario: 需求录入页提交后数据可查

- **WHEN** 用户在需求录入页提交 `projectSummary` 并触发 phase1
- **THEN** 跳转需求分析页后 `basic.projectSummary` SHALL 反映提交内容
- **AND** AI 解析产生的结构化字段 SHALL 可在各分区展示

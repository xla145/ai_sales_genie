## Why

第一阶段的需求分析已经能够生成 `需求结构化.md` 并同步到 `requirementAnalysis`，但当前后端拆分逻辑与页面实际展示字段并不完全对齐。现在需要把第一阶段产物稳定拆分为页面所需的结构化字段，确保 AI 分析结果可以直接落到“项目基础信息 / 核心要素 / 场景与诉求分析 / 功能需求 / 风险点与关注点 / 待确认需求清单 / 附件与补充说明”这些 UI 区块中，减少人工二次整理。

## What Changes

- 调整第一阶段需求分析的结构化拆分规则，使输出字段与 `RequirementAnalysisView` 页面当前展示和保存的数据结构一致。
- 明确第一阶段各章节内容如何映射到页面字段，包括基础信息、核心要素、场景、功能需求、非功能需求、约束、风险、待确认项。
- 规范场景、风险、待确认清单等列表型内容的拆分策略，确保序号、标题、正文与页面组件契合。
- 明确第一阶段输出中哪些内容进入页面直接展示字段，哪些内容保留为补充摘要或待人工确认信息。
- 补充接口与服务行为要求，保证 `POST /projects/{project_id}/phase1/run` 返回后，前端可直接读取结构化结果并展示。

## Capabilities

### New Capabilities
- `phase1-requirement-field-mapping`: 定义第一阶段需求分析结果如何拆分并映射到页面展示字段与保存结构。

### Modified Capabilities
- None.

## Impact

- 影响后端第一阶段同步逻辑：`app/api/projects.py`、`app/services/project_service.py`
- 影响前端需求分析页字段契约：`frontend/src/views/workspace/RequirementAnalysisView.vue`
- 影响需求分析结果的数据结构与列表拆分规则：`app/models/project.py` 及相关类型定义
- 影响项目第一阶段执行后的展示一致性、可编辑性与后续方案设计输入质量

## 1. 梳理目标字段契约

- [ ] 1.1 盘点 `RequirementAnalysisView` 当前使用的 `requirementAnalysis` 结构，确认基础信息、核心要素、场景、功能、风险、待确认、附件、补充说明的目标字段
- [ ] 1.2 对照 `app/models/project.py` 和前端类型定义，补齐或统一 `RequirementAnalysis` 的默认值、嵌套字段和列表项结构

## 2. 调整第一阶段结果拆分逻辑

- [ ] 2.1 在后端 phase1 同步流程中实现“章节映射 + 字段兜底”规则，将基础字段和核心字段按语义写入固定键
- [ ] 2.2 实现场景列表拆分规则，确保生成 `scenarios[]` 的 `key`、`title`、`description`、`flow`
- [ ] 2.3 实现功能需求分组映射，将内容分别写入 `functions.functionDesc`、`functions.nonFunction` 和 `functions.constraints`
- [ ] 2.4 实现风险列表拆分规则，确保生成带默认等级和顺序标题的 `risks[]`
- [ ] 2.5 实现待确认与补充说明分流规则，将 unresolved 内容写入 `pending.unknownInfo`、`pending.assumptions`、`pending.items` 或 `supplement.notes`
- [ ] 2.6 明确附件字段处理，避免在无显式元数据时自动生成伪造附件记录

## 3. 保证接口返回与页面消费一致

- [ ] 3.1 确认 `POST /projects/{project_id}/phase1/run` 在返回前已完成 `requirementAnalysis` 同步
- [ ] 3.2 校验 phase1 返回项目对象中的 `project.config.requirementAnalysis` 可被前端当前页面直接加载，无需额外转换

## 4. 补充验证与测试

- [ ] 4.1 为基础字段与核心字段映射补充后端测试，覆盖精确标题和近义语义映射场景
- [ ] 4.2 为场景、风险、待确认项等列表型拆分补充测试，覆盖默认标题、默认等级和空字段保留行为
- [ ] 4.3 为补充说明与附件兜底行为补充测试，验证未映射内容不会污染主字段
- [ ] 4.4 使用真实或近真实的 phase1 输入样例验证返回结果能够直接驱动需求分析页展示
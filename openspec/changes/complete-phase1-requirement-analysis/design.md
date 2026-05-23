## Context

当前第一阶段执行完成后，会把 AI 生成的《需求结构化.md》同步到项目配置中的 `requirementAnalysis`，供需求分析页直接展示。但页面实际使用的数据结构是以 `RequirementAnalysisView` 为中心定义的固定分区结构：`basic`、`core`、`scenarios`、`functions`、`risks`、`pending`、`attachments`、`supplement`。现有后端拆分逻辑虽然已经能写入部分字段，但没有形成一套稳定、可验证的字段映射规则，导致 AI 输出章节与页面字段之间存在语义错位、列表项结构不统一、补充信息去向不明确等问题。

这次变更需要在不改变第一阶段入口和页面主交互的前提下，明确“文档章节 -> 页面字段”的结构化映射规则，并约束列表型内容的拆分方式。相关影响点横跨后端 phase1 同步逻辑、项目模型定义、前端展示字段契约，因此需要单独设计以保证实现时不会继续依赖模糊的文本匹配。

## Goals / Non-Goals

**Goals:**
- 定义第一阶段产物到 `requirementAnalysis` 的稳定字段映射规则。
- 让 `POST /projects/{project_id}/phase1/run` 成功后返回的项目数据可直接驱动需求分析页展示。
- 统一场景、风险、待确认项等列表内容的拆分格式，保证标题、正文、序号与页面组件契合。
- 区分“直接展示字段”和“保留为补充说明/待人工确认”的内容去向，减少信息丢失或误填。
- 为后端实现与测试提供可验证的规范，避免后续页面字段调整时再次出现隐式耦合。

**Non-Goals:**
- 不重做第一阶段提示词的整体产出格式，只约束同步落库时的字段拆分与归类。
- 不扩展新的页面分区或新增复杂编辑能力。
- 不处理真实附件上传、文件解析或 OCR 能力，附件区仍仅承载记录型数据。
- 不覆盖第二阶段方案设计和后续原型流程的完整数据结构，只保证其输入来源更稳定。

## Decisions

### 1. 以页面 `RequirementAnalysis` 结构作为唯一目标契约
后端同步逻辑不再以“尽量保留原文结构”为主要目标，而是以页面当前保存结构作为唯一输出契约。也就是说，第一阶段拆分的目标不是生成一个通用摘要 JSON，而是稳定写入：
- `basic`
- `core`
- `scenarios`
- `functions.functionDesc`
- `functions.nonFunction`
- `functions.constraints`
- `risks`
- `pending`
- `attachments`
- `supplement`

这样可以让接口返回结果和页面保存结果保持同构，减少前端二次转换。

**Alternatives considered:**
- 保持后端自由结构，前端自己适配：会让页面逻辑承担解析职责，继续扩大耦合。
- 直接把完整 markdown 原文交给前端展示：无法支持页面当前的表单化编辑与保存。

### 2. 采用“章节映射 + 字段兜底”的拆分策略
优先按第一阶段文档中的业务章节进行归类，再在章节内部映射到固定字段。对于明确字段（如“项目名称”“项目背景”“性能要求”）直接落到目标键；对于无法精准命中的内容，按照语义归入：
- 业务背景类 → `core.background`
- 目标收益类 → `core.goal`
- 用户与角色类 → `core.users`
- 问题/痛点类 → `core.painPoints`
- 不确定但重要的说明 → `pending.unknownInfo` 或 `supplement.notes`

这样既保留结构化稳定性，也允许 AI 结果在章节粒度上有轻微差异。

**Alternatives considered:**
- 仅按字段名关键字精确匹配：对 AI 生成的近义表达容错不足。
- 完全依赖 LLM 二次生成 JSON：结果不稳定，且难以和现有 phase1 文档流程对齐。

### 3. 列表型内容统一拆分为“可编辑数组”
页面中的三个关键列表统一采用固定规则：
- `scenarios[]`: 每项包含 `key`、`title`、`description`、`flow`
- `risks[]`: 每项包含 `key`、`title`、`level`、`description`、`impact`、`strategy`
- `pending.items[]`: 每项包含 `title`、`text`、`checked`

拆分时：
- 序号只用于显示，不依赖文档原始编号。
- 标题缺失时按默认命名生成，如“场景1”“风险点1”。
- 正文过短或只有一句话时，优先填入 `description`/`text`，不强行拆出多字段。
- 风险等级缺失时使用页面默认值。
- `pending.items[].checked` 始终由系统初始化为 `false`。

**Alternatives considered:**
- 保存原始列表文本再由前端拆分：会让保存与展示结构不一致。
- 要求 AI 必须输出严格 JSON：对现有 phase1 产物改动过大。

### 4. 功能需求分为三组固定字典，不新增动态键
`functions` 保持页面现有的三组固定字段：
- `functionDesc`: 显性核心功能点 / 潜在功能点 / 技术选型 / 技术架构 / 依赖系统
- `nonFunction`: 性能要求 / 可用性要求 / 安全性要求 / 兼容性要求
- `constraints`: 性能约束 / 可用性约束 / 安全性约束 / 兼容性约束

第一阶段文档里明确出现的对应内容直接写入同名字段；若文档只有“要求”没有“约束”，则只填 `nonFunction`，不自动臆造 `constraints`。约束字段仅在原始需求或 AI 输出中存在明显限制条件时写入。

**Alternatives considered:**
- 把功能需求改为动态 KV：不符合当前页面组件结构。
- 自动把所有要求复制一份到约束：会制造冗余和误导。

### 5. 无法直接映射的内容进入补充或待确认区域
不是所有 phase1 内容都应该强行落到主字段。处理原则如下：
- 缺失关键信息、存在问句、需要业务方确认的内容 → `pending.unknownInfo`、`pending.assumptions` 或 `pending.items`
- 对页面主字段没有稳定归宿，但对后续设计仍有价值的备注 → `supplement.notes`
- 附件区域默认不从 phase1 文本中自动推导文件记录，除非请求中已显式携带附件元信息

这样可以避免为追求“全部结构化”而污染主字段。

### 6. 接口行为保持不变，但 phase1 返回值必须包含已同步结构化结果
不新增新的 phase1 API，而是沿用现有 `POST /projects/{project_id}/phase1/run`。执行成功后，服务层必须先完成 `requirementAnalysis` 同步，再返回项目对象，使前端刷新后即可直接读取结构化结果，而不需要额外触发二次解析接口。

**Alternatives considered:**
- 新增单独“解析 phase1 结果”接口：增加调用链和状态不一致风险。
- 只保存到磁盘不更新项目配置：前端无法直接消费。

## Risks / Trade-offs

- [页面字段未来继续变化] → 以当前 `RequirementAnalysis` 结构为契约，同时在规范中显式列出目标字段，后续字段变更时同步更新映射规则与测试。
- [AI 输出章节命名不稳定] → 使用“章节语义映射 + 字段兜底”而不是完全依赖固定标题。
- [列表内容信息量不足，难以完整拆分] → 允许只填核心字段，缺失部分保留默认值或空值，不强行补全。
- [把不确定信息错误写入正式字段] → 将问句、假设、限制不明内容优先落入 pending/supplement，而不是主字段。
- [前后端默认值不一致] → 通过统一模型默认值与测试样例，确保空数组、默认标题、默认等级等行为一致。

## Migration Plan

1. 梳理并固化当前页面所需的 `RequirementAnalysis` 目标结构。
2. 调整后端 phase1 同步逻辑，将 markdown/文本章节映射到该结构。
3. 如有必要，补充项目模型或类型定义，确保后端返回值与前端字段一致。
4. 增加覆盖基础字段、列表字段、兜底字段的测试样例。
5. 使用真实 phase1 示例验证返回的 `project.config.requirementAnalysis` 可直接渲染页面。
6. 若发现历史项目缺少新字段，继续依赖前端/后端现有 normalize 默认值兜底，不需要单独迁移脚本。

## Open Questions

- 第一阶段提示词中是否需要同步补充更清晰的章节命名，以进一步降低解析歧义。
- `industry`、`projectType`、`keywords` 这类基础字段在原始需求中缺失时，是否需要从项目主信息或已有配置做补齐。
- `pending.assumptions` 与 `supplement.notes` 的边界是否还需要更细的语义约束，以避免内容分流不一致。
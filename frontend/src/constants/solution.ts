export type SolutionViewMode = 'overview' | 'prd' | 'functions' | 'presentation'
export type PresentationMode = 'prototype' | 'ppt'
export type TaskStatus = 'pending' | 'running' | 'done' | 'error'

export interface GenerationTask {
  id: string
  name: string
  description: string
  status: TaskStatus
  icon: string
  startedAt?: number
  finishedAt?: number
  durationMs?: number
}

export interface SolutionSlideItem {
  id: number
  title: string
  points: string[]
}

export interface SolutionFunctionItem {
  module: string
  level1: string
  level2: string
  point: string
  description: string
  fields: string
  interaction: string
  constraints: string
}

export interface PrototypeFileItem {
  language: string
  content: string
}

export const INIT_GENERATION_TASKS: GenerationTask[] = [
  { id: 'prd', name: 'PRD 需求文档', description: '基于需求分析生成完整的产品需求文档', status: 'pending', icon: '📄' },
  { id: 'functions', name: '功能清单', description: '拆解功能模块、优先级及验收标准', status: 'pending', icon: '✅' },
  { id: 'prototype', name: '交互原型', description: '生成可交互的 HTML/CSS/JS 原型代码', status: 'pending', icon: '🎨' },
]

export const SOLUTION_PPT_SLIDES: SolutionSlideItem[] = [
  {
    id: 1,
    title: '行业背景与痛点',
    points: ['人工客服成本持续攀升', '响应速度无法满足 24/7 需求', '传统机器人语义理解薄弱'],
  },
  {
    id: 2,
    title: '核心技术优势',
    points: ['自研 LLM 智能算法', '多步骤意图识别', '多终端无缝同步'],
  },
  {
    id: 3,
    title: '业务价值转化',
    points: ['人工成本直降 35%', '首次解决率提升 40%', '用户净推荐值 (NPS) +15'],
  },
]

export const SOLUTION_FUNCTION_LIST: SolutionFunctionItem[] = [
  {
    module: '智能路由',
    level1: '意图识别',
    level2: '自然语言处理',
    point: '多意图分发识别',
    description: '支持嵌套意图分析的智能路由，通过Transformer架构处理复杂请求',
    fields: 'userId, queryText, contextId',
    interaction: '用户输入 -> NLU解析 -> 多步任务生成 -> 分发',
    constraints: '延迟需控制在 200ms 以内',
  },
  {
    module: '交互中心',
    level1: '实时对话',
    level2: '富媒体交互',
    point: '卡片式动态组件',
    description: '支持工单、商品、物流信息的结构化展示，通过JSON DSL协议定义卡片语义变量',
    fields: 'cardType, payload, sessionId',
    interaction: 'AI生成 -> 卡片渲染 -> 用户选择 -> 反馈',
    constraints: '卡片模板需符合企业视觉规范',
  },
]

export const PROTOTYPE_FILES: Record<string, PrototypeFileItem> = {
  'index.html': {
    language: 'html',
    content: `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>智能客服助手</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="chat-container">
    <div class="chat-header">
      <div class="chat-title">智能客服助手</div>
      <div class="chat-status">● 在线服务中</div>
    </div>
    <div class="chat-body" id="chatBody">
      <div class="message bot">
        <div class="avatar bot-avatar"></div>
        <div class="message-content">
          您好！我是智能客服助手，有什么可以帮到您的吗？
        </div>
      </div>
    </div>
    <div class="input-area">
      <input type="text" id="userInput" placeholder="输入您的问题..." />
      <button onclick="sendMessage()">发送</button>
    </div>
  </div>
  <script src="script.js"></script>
</body>
</html>`,
  },
  'style.css': {
    language: 'css',
    content: `* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

.chat-container {
  width: 100%;
  max-width: 900px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 80vh;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 28px 32px;
  flex-shrink: 0;
}

.chat-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 6px;
}

.chat-status {
  font-size: 13px;
  opacity: 0.85;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.message.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  flex-shrink: 0;
}

.bot-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.user-avatar {
  background: #cbd5e1;
}

.message-content {
  padding: 14px 18px;
  border-radius: 18px;
  max-width: 60%;
  font-size: 14px;
  line-height: 1.6;
}

.bot .message-content {
  background: #f1f5f9;
  color: #1e293b;
  border-top-left-radius: 4px;
}

.user .message-content {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-top-right-radius: 4px;
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 20px 32px;
  border-top: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.input-area input {
  flex: 1;
  padding: 14px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.input-area input:focus {
  border-color: #667eea;
}

.input-area button {
  padding: 14px 28px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
}`,
  },
  'script.js': {
    language: 'javascript',
    content: `const botReplies = [
  '感谢您的提问！我正在为您查询相关信息...',
  '根据您的描述，我建议您可以尝试以下方案：\\n1. 检查网络连接\\n2. 刷新页面重试\\n3. 联系技术支持',
  '您好！这个问题我来帮您解答。我们的产品支持多种集成方式，请告诉我您使用的技术栈？',
  '明白了！我为您转接专业的技术顾问，请稍等片刻。',
];

let replyIndex = 0;

function sendMessage() {
  const input = document.getElementById('userInput');
  const chatBody = document.getElementById('chatBody');
  const text = input.value.trim();
  if (!text) return;

  const userMsg = document.createElement('div');
  userMsg.className = 'message user';
  userMsg.innerHTML = \`
    <div class="avatar user-avatar"></div>
    <div class="message-content">\${text}</div>
  \`;
  chatBody.appendChild(userMsg);
  input.value = '';
  chatBody.scrollTop = chatBody.scrollHeight;

  setTimeout(() => {
    const botMsg = document.createElement('div');
    botMsg.className = 'message bot';
    botMsg.innerHTML = \`
      <div class="avatar bot-avatar"></div>
      <div class="message-content">\${botReplies[replyIndex % botReplies.length]}</div>
    \`;
    chatBody.appendChild(botMsg);
    chatBody.scrollTop = chatBody.scrollHeight;
    replyIndex++;
  }, 800);
}

document.getElementById('userInput').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});`,
  },
  'config.json': {
    language: 'json',
    content: `{
  "project": "智能客服助手",
  "version": "1.0.0",
  "description": "基于规则引擎的智能客服对话界面原型",
  "settings": {
    "theme": {
      "primary": "#667eea",
      "secondary": "#764ba2",
      "background": "#f5f7fa"
    },
    "bot": {
      "name": "智能客服助手",
      "replyDelay": 800,
      "maxHistory": 50
    },
    "ui": {
      "maxWidth": "900px",
      "borderRadius": "20px",
      "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    }
  }
}`,
  },
}

export const PROTOTYPE_QUICK_COMMANDS = [
  { label: '改颜色', msg: '把标题改成紫色', reply: '我已经将标题颜色调整为紫色，请查看右侧预览效果。' },
  { label: '加搜索', msg: '增加一个搜索框', reply: '我已经在顶部添加了搜索框，请查看右侧预览效果。' },
  { label: '调圆角', msg: '圆角改大一点', reply: '我已经将圆角调整为更大的弧度，请查看右侧预览效果。' },
]

export const TASK_STEP_COLORS = [
  {
    border: 'border-blue-200',
    activeBorder: 'border-blue-400 bg-blue-50',
    bg: 'bg-blue-600',
    activeBg: 'bg-blue-500',
    btn: 'bg-blue-600 hover:bg-blue-700',
    outlineBtn: 'border-blue-600 text-blue-600 hover:bg-blue-50',
    bar: 'bg-blue-100 text-blue-700',
    viewMode: 'prd' as SolutionViewMode,
  },
  {
    border: 'border-green-200',
    activeBorder: 'border-green-400 bg-green-50',
    bg: 'bg-green-600',
    activeBg: 'bg-green-500',
    btn: 'bg-green-600 hover:bg-green-700',
    outlineBtn: 'border-green-600 text-green-600 hover:bg-green-50',
    bar: 'bg-green-100 text-green-700',
    viewMode: 'functions' as SolutionViewMode,
  },
  {
    border: 'border-purple-200',
    activeBorder: 'border-purple-400 bg-purple-50',
    bg: 'bg-purple-600',
    activeBg: 'bg-purple-500',
    btn: 'bg-purple-600 hover:bg-purple-700',
    outlineBtn: 'border-purple-600 text-purple-600 hover:bg-purple-50',
    bar: 'bg-purple-100 text-purple-700',
    viewMode: 'presentation' as SolutionViewMode,
  },
]

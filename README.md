# Hermes Validation Backend

这是一个用于验证 `Python + FastAPI + Hermes` 集成方式的最小后端项目。

当前目标是验证以下几点：

- 可以创建多个项目
- 每个项目有独立目录、独立运行记录、独立日志
- 一个项目的运行不会影响另一个项目
- 可以查询项目运行状态和运行日志

## 目录结构

```text
hermes_test/
├── app/
│   ├── api/
│   ├── clients/
│   ├── models/
│   ├── services/
│   └── storage/
├── data/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 环境配置

先复制示例配置：

```bash
cp .env.example .env
```

然后编辑 `.env`：

```env
LLM_PROVIDER=hermes
LLM_BASE_URL=http://127.0.0.1:8642
LLM_API_KEY=your_key
LLM_MODEL=
LLM_TIMEOUT=120

# 兼容保留，未设置 LLM_* 时仍可回退读取
HERMES_BASE_URL=http://127.0.0.1:8642
HERMES_API_KEY=your_key
```

说明：

- 当前执行引擎 / provider 只在**服务启动时**通过环境变量确定
- 运行中的 API 请求不会再允许手动切换 provider
- 推荐优先配置 `LLM_*`
- `HERMES_*` 目前作为兼容保留项存在

## 安装依赖

如果当前项目虚拟环境还没装依赖：

```bash
uv pip install --python .venv/bin/python -r requirements.txt
```

## 启动服务

启动前请确认 `.env` 中已经设置好启动期固定配置，例如：

- `LLM_PROVIDER`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_TIMEOUT`


```bash
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
```

启动后可访问：

```bash
curl http://127.0.0.1:8011/health
```

预期返回：

```json
{"status":"ok"}
```

## 已实现接口

### 创建项目

```http
POST /projects
```

### 查询项目列表

```http
GET /projects
```

### 查询项目详情

```http
GET /projects/{project_id}
```

### 启动项目运行

```http
POST /projects/{project_id}/runs
```

### 查询项目运行列表

```http
GET /projects/{project_id}/runs
```

### 查询单次运行详情

```http
GET /projects/{project_id}/runs/{run_id}
```

### 删除项目

```http
DELETE /projects/{project_id}
```

### 查询运行日志

```http
GET /projects/{project_id}/runs/{run_id}/logs
```

## curl 验证示例

下面是一组可以直接手工执行的验证步骤。

### 1. 创建项目 A

```bash
curl -X POST http://127.0.0.1:8011/projects \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "project-a",
    "config": {
      "prompt": "say A"
    }
  }'
```

### 2. 创建项目 B

```bash
curl -X POST http://127.0.0.1:8011/projects \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "project-b",
    "config": {
      "prompt": "say B"
    }
  }'
```

返回中记录两个 `project_id`。

### 3. 查询项目列表

```bash
curl http://127.0.0.1:8011/projects
```

### 4. 启动项目 A 运行

将 `proj_xxx` 替换为真实项目 ID：

```bash
curl -X POST http://127.0.0.1:8011/projects/proj_xxx/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "fail": false
  }'
```

返回中记录 `run_id`。

### 5. 启动项目 B 失败运行

```bash
curl -X POST http://127.0.0.1:8011/projects/proj_yyy/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "fail": true
  }'
```

### 5.1 启动一个长时间运行任务（用于验证删除冲突）

```bash
curl -X POST http://127.0.0.1:8011/projects/proj_xxx/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "fail": false,
    "sleep_seconds": 5
  }'
```

说明：

- `sleep_seconds` 可用于让任务保持运行一段时间
- 便于验证“运行中删除项目会返回 409”

### 6. 查询项目 A 的运行详情

```bash
curl http://127.0.0.1:8011/projects/proj_xxx/runs/run_xxx
```

### 7. 查询项目 B 的运行详情

```bash
curl http://127.0.0.1:8011/projects/proj_yyy/runs/run_yyy
```

### 8. 查询项目 A 日志

```bash
curl http://127.0.0.1:8011/projects/proj_xxx/runs/run_xxx/logs
```

### 9. 查询项目 B 日志

```bash
curl http://127.0.0.1:8011/projects/proj_yyy/runs/run_yyy/logs
```

### 10. 删除项目

```bash
curl -X DELETE http://127.0.0.1:8011/projects/proj_xxx -i
```

删除成功时返回：

```http
HTTP/1.1 204 No Content
```

如果项目还有运行中的任务，预期返回：

```http
HTTP/1.1 409 Conflict
```

你可以结合上面的 `sleep_seconds` 场景验证这个返回。

## 运行结果说明

### 成功场景

成功时，运行详情里通常会有：

- `status: success`
- `result_summary.output_file`
- `result_summary.content_preview`

### 失败场景

失败时，运行详情里通常会有：

- `status: failed`
- `error_message`

### Hermes 不可用时

如果使用的是 `LLM_PROVIDER=hermes`，则服务启动后所有 run / workflow 都会固定使用该 provider。


如果 Hermes 服务不可达，或者 Hermes 服务端没有正确配置模型，当前原型仍然可以完成链路验证：

- 后端服务仍会记录日志
- 项目隔离仍成立
- 运行状态仍可查询
- 某些场景下会回退到 mock 输出
- 某些场景下 Hermes 会返回错误信息并被写入输出/日志

## 数据落盘位置

每个项目的数据都保存在：

```text
data/projects/{project_id}/
```

其中包括：

- `project.json` 项目元数据
- `config.json` 项目配置
- `runs/*.json` 每次运行记录
- `logs/*.log` 每次运行日志
- `outputs/*` 运行输出文件

## 当前限制

这是验证版，不是最终正式系统。当前有这些限制：

- 使用文件系统存储，没有数据库
- 没有鉴权
- 没有任务取消
- 没有 WebSocket 实时日志推送
- 运行状态管理还是最小实现

## 下一步建议

后续可以继续补：

- 更标准的状态机
- 数据库存储
- `.env` 配置校验
- 更完整的 Hermes 调用错误分类
- 前端页面或 Swagger 使用说明

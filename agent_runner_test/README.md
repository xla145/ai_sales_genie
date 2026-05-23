# agent_runner_test

基于 `doc/技术方案.md` 生成的最小可运行测试项目。

## 目录结构

```text
agent_runner_test/
  agent_runner/
    api/
      projects.py
      runs.py
      events.py
    db/
      base.py
      session.py
      models.py
    services/
      project_service.py
      run_service.py
      hermes_service.py
      requirement_service.py
      artifact_service.py
      event_service.py
    storage/
      local_storage.py
      s3_storage.py
    worker/
      runner.py
    config.py
    main.py
  requirements.txt
  .env.example
  run.py
```

## 快速启动

1. 创建虚拟环境并安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 配置环境变量

```bash
cp .env.example .env
```

3. 启动服务

```bash
python run.py
```

4. 验证接口

- 健康检查：`GET http://127.0.0.1:8081/health`
- 项目创建：`POST http://127.0.0.1:8081/projects`
- Run 创建：`POST http://127.0.0.1:8081/runs`
- 事件查询：`GET http://127.0.0.1:8081/events/{run_id}`

## 说明

- 这个版本是“测试骨架版”：
  - 表结构模型已按方案落地到 `agent_runner/db/models.py`
  - API 与 service 先提供最小回包，便于你压测或联调
- 下一步可以加：
  - Alembic migration 初始化
  - 真正的 MySQL CRUD
  - SSE 增量事件流
  - Hermes 实际调用与 patch 入库流程

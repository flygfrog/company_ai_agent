# Company AI Agent

本项目是尧唐科技暑期实习期间推进的公司内部 AI Agent 原型。当前目标是通过钉钉机器人接收用户消息，转发到本地 FastAPI 后端，由后端识别用户意图并调用大模型生成规范实习日报。

目前项目已经完成从“本地接口验证”到“钉钉机器人 + OpenClaw + FastAPI + DeepSeek API 联调”的最小闭环，下一阶段将继续完善钉钉侧稳定性、权限配置、日志追踪、部署和更多工具能力。

## 7/14 当前进度

已完成：

1. 搭建 Python FastAPI 后端服务。
2. 接入 DeepSeek API，并保留本地 mock 模式用于开发和测试。
3. 实现日报生成核心逻辑，将 prompt、Agent 调度和接口入口拆分到不同模块。
4. 新增统一聊天入口 `/chat`，支持简单意图识别。
5. 新增健康检查 `/health` 和版本信息 `/version` 接口。
6. 增加统一日志记录、请求 request_id 和业务异常处理。
7. 完成 OpenClaw 自定义 Skill 调用本地 FastAPI 的端到端测试。
8. 完成 pytest 自动化测试，当前覆盖健康检查、日报接口、聊天接口和意图提取逻辑。

当前支持的主要功能：

- 用户发送 `生成日报：今天完成了……`
- 后端识别为日报生成意图
- 调用 mock 回复或 DeepSeek API
- 返回结构化实习日报

## 项目结构

```text
company_ai_agent/
├── docs/                 # 项目方案、调研、技术方案和实习笔记
├── logs/                 # 运行日志
├── src/
│   ├── agent.py          # 日报生成 Agent 调度逻辑
│   ├── config.py         # 环境变量和配置读取
│   ├── exceptions.py     # 自定义异常
│   ├── llm_client.py     # DeepSeek API 调用封装
│   ├── logging_config.py # 日志配置
│   ├── main.py           # FastAPI 应用和接口入口
│   └── prompts.py        # 日报生成 prompt
├── tests/                # pytest 测试用例
├── .env.example          # 环境变量示例
├── pytest.ini            # pytest 配置
├── requirements.txt      # Python 依赖
└── README.md
```

## 环境配置

建议使用 Python 3.11 及以上版本。

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
pip install -r requirements.txt
```

复制 `.env.example` 为 `.env`，并按需修改：

```env
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
USE_MOCK_LLM=true
```

说明：

- `USE_MOCK_LLM=true`：使用本地模拟日报，适合开发和测试。
- `USE_MOCK_LLM=false`：调用真实 DeepSeek API，需要配置有效的 `DEEPSEEK_API_KEY`。

## 启动服务

在项目根目录运行：

```powershell
python -m uvicorn src.main:app --reload --port 8000
```

启动后可以访问：

- 接口文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`
- 版本信息：`http://127.0.0.1:8000/version`

## 接口说明

### GET /

检查后端是否启动。

### GET /health

返回服务健康状态。

### GET /version

返回服务版本、服务名和当前是否启用 mock LLM。

### POST /daily-report

直接根据工作内容生成日报。

请求示例：

```json
{
  "text": "今天完成了 FastAPI 后端搭建，并接入了 DeepSeek API。"
}
```

### POST /chat

统一聊天入口，后续钉钉机器人消息可以统一转发到该接口。

请求示例：

```json
{
  "text": "生成日报：今天完成了 OpenClaw Skill 创建，并测试了本地 FastAPI 调用。",
  "user_id": "test_user",
  "source": "dingtalk"
}
```

当前 `/chat` 支持：

1. 问候语：如 `你好`、`hello`。
2. 日报生成：如 `生成日报：今天完成了……`。
3. 未知意图提示：提醒用户当前暂时支持日报生成功能。

## 测试

在项目文件夹下powershell下先启动虚拟环境，再运行全部测试：

```powershell
pytest
```

当前测试覆盖：

- `/`、`/health`、`/version`
- `/daily-report` 成功、空输入、缺少字段
- `/chat` 问候、日报生成、缺少日报内容、未知意图
- 日报意图提取函数 `extract_daily_report_content`

最近一次记录的测试结果为：

```text
15 passed, 1 warning
```

## 钉钉与 OpenClaw 联调状态

当前已经完成一次端到端联调：

```text
钉钉消息
→ OpenClaw 接收
→ 自定义 Skill 转发到 FastAPI /chat
→ 后端识别日报意图
→ 调用 DeepSeek API
→ 返回规范日报到钉钉
```

调试时常用命令：

```powershell
python -m uvicorn src.main:app --reload --port 8000
openclaw logs --follow
```

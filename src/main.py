from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.config import APP_NAME, USE_MOCK_LLM
from src.agent import generate_daily_report


app = FastAPI(title=APP_NAME)


class DailyReportRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class DailyReportResponse(BaseModel):
    reply: str


class ChatRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    user_id: str | None = None
    source: str | None = "local"


class ChatResponse(BaseModel):
    reply: str


def build_mock_daily_report(text: str) -> str:

    return f"""### 今日目标

1. 继续推进公司 AI Agent 项目，重点完成日报生成最小功能。
2. 验证 FastAPI 后端与大模型调用流程是否稳定。

### 完成事项

1. 接收用户输入的工作内容。
2. 按固定格式生成实习日报。
3. 完成本地日报生成接口测试。

### 遇到的问题

当前处于本地测试阶段，暂未接入钉钉消息转发。

### 解决过程

先使用 FastAPI 接口验证“输入工作内容 → 输出规范日报”的基础链路，确保后端功能独立可用。

### 明日计划

1. 继续优化日报生成 prompt。
2. 将钉钉机器人消息接入 FastAPI 后端。
3. 测试钉钉输入内容后自动返回日报。

原始输入：
{text}
"""

@app.get("/")
def root():
    return {
        "message": "Company AI Agent backend is running.",
        "mock_llm": USE_MOCK_LLM,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": APP_NAME,
    }


@app.post("/daily-report", response_model=DailyReportResponse)
def daily_report(request: DailyReportRequest):
    if USE_MOCK_LLM:
        reply = build_mock_daily_report(request.text)
    else:
        reply = generate_daily_report(request.text)

    return DailyReportResponse(reply=reply)
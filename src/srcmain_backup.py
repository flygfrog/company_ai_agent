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


def extract_daily_report_content(text: str) -> str | None:
    """
    判断用户是否想生成日报。
    如果是，返回去掉命令词后的工作内容。
    如果不是，返回 None。
    """

    text = text.strip()

    prefixes = [
        "生成日报",
        "日报",
        "帮我生成日报",
        "帮我写日报",
        "整理日报",
        "实习日报",
        "生成实习日报",
    ]

    for prefix in prefixes:
        if text.startswith(prefix):
            content = text[len(prefix):].strip()
            content = content.lstrip("：:，,。.\n ")
            return content

    return None


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


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    统一聊天入口。
    后续钉钉机器人收到的消息可以统一转发到这里。
    """

    text = request.text.strip()

    # 1. 简单问候
    if text in ["你好", "您好", "hello", "Hello", "hi", "Hi"]:
        return ChatResponse(
            reply=(
                "你好，我是公司 AI Agent 助手。\n\n"
                "当前支持的功能：\n"
                "发送“生成日报：今天完成了……”即可生成规范实习日报。"
            )
        )

    # 2. 日报生成意图
    daily_report_content = extract_daily_report_content(text)

    if daily_report_content is not None:
        if not daily_report_content:
            return ChatResponse(
                reply=(
                    "请在“生成日报”后面输入今天的工作内容。\n\n"
                    "示例：生成日报：今天配置了 OpenClaw，搭建了 FastAPI 后端，并测试了 DeepSeek API。"
                )
            )

        if USE_MOCK_LLM:
            reply = build_mock_daily_report(daily_report_content)
        else:
            reply = generate_daily_report(daily_report_content)

        return ChatResponse(reply=reply)

    # 3. 其他暂不支持的输入
    return ChatResponse(
        reply=(
            "当前暂时支持日报生成功能。\n\n"
            "你可以这样输入：\n"
            "生成日报：今天完成了 OpenClaw 配置、FastAPI 后端搭建和 DeepSeek API 接入测试。"
        )
    )
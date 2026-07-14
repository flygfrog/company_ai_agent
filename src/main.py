import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agent import generate_daily_report
from src.config import APP_NAME, USE_MOCK_LLM
from src.exceptions import AppException
from src.logging_config import setup_logging


setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
)


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


def get_request_id(request: Request) -> str:
    """从请求对象中取得 request_id。"""

    return getattr(request.state, "request_id", "unknown")


def validate_text(text: str, field_name: str = "输入内容") -> str:
    """去除首尾空白并检查内容是否为空。"""

    cleaned_text = text.strip()

    if not cleaned_text:
        raise AppException(
            message=f"{field_name}不能为空",
            status_code=400,
            error_code="EMPTY_INPUT",
        )

    return cleaned_text


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

    如果是，返回去掉命令词后的工作内容；
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


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """记录每个 HTTP 请求的路径、状态码和耗时。"""

    request_id = uuid.uuid4().hex[:8]
    request.state.request_id = request_id
    start_time = time.perf_counter()

    logger.info(
        "请求开始 | request_id=%s | method=%s | path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "请求结束 | request_id=%s | status_code=%d | duration_ms=%.2f",
            request_id,
            response.status_code,
            duration_ms,
        )

        return response

    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "请求处理异常 | request_id=%s | duration_ms=%.2f",
            request_id,
            duration_ms,
        )
        raise


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """处理主动抛出的业务异常。"""

    request_id = get_request_id(request)

    logger.warning(
        "业务异常 | request_id=%s | path=%s | code=%s | message=%s",
        request_id,
        request.url.path,
        exc.error_code,
        exc.message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            },
            "request_id": request_id,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """处理请求参数校验异常。"""

    request_id = get_request_id(request)
    details = jsonable_encoder(exc.errors())

    logger.warning(
        "参数校验失败 | request_id=%s | path=%s | errors=%s",
        request_id,
        request.url.path,
        details,
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求参数格式不正确",
                "details": details,
            },
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理未预料到的服务器内部异常。"""

    request_id = get_request_id(request)

    logger.exception(
        "未处理异常 | request_id=%s | path=%s",
        request_id,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误，请稍后重试",
            },
            "request_id": request_id,
        },
    )


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


@app.get("/version")
def get_version():
    return {
        "version": app.version,
        "service": APP_NAME,
        "mock_llm": USE_MOCK_LLM,
    }


@app.post("/daily-report", response_model=DailyReportResponse)
def daily_report(request: DailyReportRequest):
    text = validate_text(request.text, "工作内容")

    logger.info(
        "收到日报生成请求 | mode=%s | input_length=%d",
        "mock" if USE_MOCK_LLM else "deepseek",
        len(text),
    )

    if USE_MOCK_LLM:
        reply = build_mock_daily_report(text)
    else:
        reply = generate_daily_report(text)

    return DailyReportResponse(reply=reply)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    统一聊天入口。

    后续钉钉机器人收到的消息可以统一转发到这里。
    """

    text = validate_text(request.text, "聊天消息")

    logger.info(
        "收到聊天请求 | source=%s | input_length=%d",
        request.source or "unknown",
        len(text),
    )

    if text.lower() in ["你好", "您好", "hello", "hi"]:
        logger.info("聊天意图识别完成 | intent=greeting")

        return ChatResponse(
            reply=(
                "你好，我是公司 AI Agent 助手。\n\n"
                "当前支持的功能：\n"
                "发送“生成日报：今天完成了……”即可生成规范实习日报。"
            )
        )

    daily_report_content = extract_daily_report_content(text)

    if daily_report_content is not None:
        logger.info("聊天意图识别完成 | intent=daily_report")

        if not daily_report_content:
            raise AppException(
                message=(
                    "请在“生成日报”后面输入今天的工作内容。"
                    "示例：生成日报：今天搭建了 FastAPI 后端。"
                ),
                status_code=400,
                error_code="MISSING_DAILY_REPORT_CONTENT",
            )

        if USE_MOCK_LLM:
            reply = build_mock_daily_report(daily_report_content)
        else:
            reply = generate_daily_report(daily_report_content)

        return ChatResponse(reply=reply)

    logger.info("聊天意图识别完成 | intent=unknown")

    return ChatResponse(
        reply=(
            "当前暂时支持日报生成功能。\n\n"
            "你可以这样输入：\n"
            "生成日报：今天完成了 OpenClaw 配置、FastAPI 后端搭建和 DeepSeek API 接入测试。"
        )
    )

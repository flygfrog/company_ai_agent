import logging

from src.exceptions import AppException
from src.llm_client import call_deepseek
from src.prompts import (
    DAILY_REPORT_SYSTEM_PROMPT,
    build_daily_report_user_prompt,
)


logger = logging.getLogger(__name__)

MAX_WORK_CONTENT_LENGTH = 5000


def generate_daily_report(text: str) -> str:
    """
    根据用户输入的工作内容生成规范日报。

    参数：
        text: 用户输入的工作内容。

    返回：
        大模型生成的日报文本。

    异常：
        AppException: 输入为空或内容过长。
        LLMServiceError: DeepSeek API 调用失败。
    """

    if not isinstance(text, str):
        raise AppException(
            message="工作内容格式不正确",
            status_code=400,
            error_code="INVALID_WORK_CONTENT",
        )

    cleaned_text = text.strip()

    if not cleaned_text:
        raise AppException(
            message="工作内容不能为空",
            status_code=400,
            error_code="EMPTY_WORK_CONTENT",
        )

    if len(cleaned_text) > MAX_WORK_CONTENT_LENGTH:
        raise AppException(
            message=f"工作内容过长，请控制在 {MAX_WORK_CONTENT_LENGTH} 字以内",
            status_code=400,
            error_code="WORK_CONTENT_TOO_LONG",
        )

    logger.info(
        "开始生成日报 | input_length=%d",
        len(cleaned_text),
    )

    messages = [
        {
            "role": "system",
            "content": DAILY_REPORT_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": build_daily_report_user_prompt(cleaned_text),
        },
    ]

    report = call_deepseek(messages)

    logger.info(
        "日报生成完成 | output_length=%d",
        len(report),
    )

    return report
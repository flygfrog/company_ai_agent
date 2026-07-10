import logging

from openai import OpenAI

from src.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL
)


from src.exceptions import LLMServiceError


logger = logging.getLogger(__name__)


def call_deepseek(messages: list[dict]) -> str:
    """
    调用 DeepSeek API。

    参数：
        messages: OpenAI 兼容格式的消息列表。

    返回：
        DeepSeek 返回的文本内容。

    异常：
        LLMServiceError: API 配置错误、调用失败或返回内容为空。
    """

    if not DEEPSEEK_API_KEY:
        logger.error("未配置 DEEPSEEK_API_KEY，请检查 .env 文件。")
        raise LLMServiceError("大模型服务暂时不可用，请联系管理员。")

    logger.info(
        "开始调用 DeepSeek API | model=%s | message_count=%d",
        DEEPSEEK_MODEL,
        len(messages),
    )

    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )

        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            stream=False,
            extra_body={
                "thinking": {
                    "type": "disabled",
                }
            },
        )

        content = response.choices[0].message.content

        if not content or not content.strip():
            logger.error("DeepSeek API 返回内容为空")
            raise LLMServiceError("大模型返回内容为空，请稍后重试")

        logger.info(
            "DeepSeek API 调用成功 | response_length=%d",
            len(content),
        )

        return content.strip()

    except LLMServiceError:
        # 已经处理过的业务异常直接继续抛出
        raise

    except Exception:
        # 自动记录异常类型、错误信息和完整调用栈
        logger.exception(
            "DeepSeek API 调用失败 | model=%s",
            DEEPSEEK_MODEL,
        )
        raise LLMServiceError("大模型服务暂时不可用，请稍后重试")
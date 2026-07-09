from openai import OpenAI

from src.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL
)


def call_deepseek(messages: list[dict]) -> str:
    """
    调用 DeepSeek API。
    """

    if not DEEPSEEK_API_KEY:
        raise ValueError("未配置 DEEPSEEK_API_KEY，请检查 .env 文件。")

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
                "type": "disabled"
            }
        },
    )

    return response.choices[0].message.content or ""
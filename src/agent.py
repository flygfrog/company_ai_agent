# src/agent.py

from src.llm_client import call_deepseek
from src.prompts import DAILY_REPORT_SYSTEM_PROMPT, build_daily_report_user_prompt


def generate_daily_report(text: str) -> str:
    """
    根据用户输入的工作内容生成规范日报。
    """

    messages = [
        {
            "role": "system",
            "content": DAILY_REPORT_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": build_daily_report_user_prompt(text),
        },
    ]

    return call_deepseek(messages)
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Company AI Agent"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek--v4-flash")

USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "true").lower() == "true"
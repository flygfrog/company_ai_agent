import os

import pytest
from fastapi.testclient import TestClient

# 测试时强制使用 mock 模式，避免每次 pytest 都调用真实 DeepSeek API
os.environ["USE_MOCK_LLM"] = "true"

from src.main import app  # noqa: E402


@pytest.fixture()
def client():
    return TestClient(app)
def test_chat_greeting(client):
    response = client.post(
        "/chat",
        json={
            "text": "你好",
            "source": "pytest",
            "user_id": "test_user",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "reply" in data
    assert "公司 AI Agent 助手" in data["reply"]
    assert "生成日报" in data["reply"]


def test_chat_generate_daily_report(client):
    response = client.post(
        "/chat",
        json={
            "text": "生成日报：今天完成了 pytest 自动化测试。",
            "source": "pytest",
            "user_id": "test_user",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "reply" in data
    assert "今日目标" in data["reply"]
    assert "完成事项" in data["reply"]
    assert "今天完成了 pytest 自动化测试" in data["reply"]


def test_chat_missing_daily_report_content(client):
    response = client.post(
        "/chat",
        json={
            "text": "生成日报",
            "source": "pytest",
            "user_id": "test_user",
        },
    )

    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "MISSING_DAILY_REPORT_CONTENT"
    assert "请在“生成日报”后面输入今天的工作内容" in data["error"]["message"]


def test_chat_unknown_intent(client):
    response = client.post(
        "/chat",
        json={
            "text": "帮我查一下公司制度",
            "source": "pytest",
            "user_id": "test_user",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "reply" in data
    assert "当前暂时支持日报生成功能" in data["reply"]
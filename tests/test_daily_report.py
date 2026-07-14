def test_daily_report_success(client):
    response = client.post(
        "/daily-report",
        json={
            "text": "今天完成了 FastAPI 健康检查接口，并开始建立 pytest 自动化测试。"
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "reply" in data
    assert "今日目标" in data["reply"]
    assert "完成事项" in data["reply"]
    assert "原始输入" in data["reply"]


def test_daily_report_empty_text(client):
    response = client.post(
        "/daily-report",
        json={
            "text": "   "
        },
    )

    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "EMPTY_INPUT"


def test_daily_report_missing_text_field(client):
    response = client.post(
        "/daily-report",
        json={},
    )

    assert response.status_code == 422

    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
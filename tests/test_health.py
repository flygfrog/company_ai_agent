def test_root(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Company AI Agent backend is running."
    assert "mock_llm" in data


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Company AI Agent"


def test_version(client):
    response = client.get("/version")

    assert response.status_code == 200

    data = response.json()
    assert data["version"] == "0.1.0"
    assert data["service"] == "Company AI Agent"
    assert "mock_llm" in data
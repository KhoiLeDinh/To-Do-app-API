import time
def test_get_todos_without_token_returns_401(client):
    response = client.get("/api/v1/todos")
    assert response.status_code == 401


def test_register_login_and_create_todo(client):
    user_payload = {
        "username": "testuser",
        "password": "strongpassword123",
    }
    register_res = client.post("/api/v1/register", json=user_payload)
    assert register_res.status_code in (200, 201)

    login_res = client.post("/api/v1/login", json=user_payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    todo_res = client.post(
        "/api/v1/todos",
        json={"title": "First test"},
        headers=headers,
    )
    assert todo_res.status_code in (200, 201)
    assert todo_res.json()["title"] == "First test"

def test_login_rate_limit_blocks_after_max_requests(client, monkeypatch):
    # Cố định thời gian trong cùng 1 cửa sổ
    monkeypatch.setattr(time, "time", lambda: 1_700_000_000.0)

    payload = {
        "username": "nobody",
        "password": "wrongpassword",
    }

    for _ in range(5):
        res = client.post("/api/v1/login", json=payload)
        assert res.status_code != 429

    blocked_res = client.post("/api/v1/login", json=payload)
    assert blocked_res.status_code == 429
    assert blocked_res.json()["detail"] == "Too many requests"
    assert "Retry-After" in blocked_res.headers
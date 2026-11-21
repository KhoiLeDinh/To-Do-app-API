def test_get_todos_without_token_returns_401(client):
    response = client.get("/api/v1/todos")
    assert response.status_code == 401


def test_register_login_and_create_todo(client):
    user_payload = {
        "username": "testuser",
        "password": "strongpassword123",
    }
    register_res = client.post("/api/v1/auth/register", json=user_payload)
    assert register_res.status_code in (200, 201)

    login_res = client.post("/api/v1/auth/login", json=user_payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    todo_res = client.post(
        "/api/v1/todos",
        json={"title": "Viết test đầu tiên"},
        headers=headers,
    )
    assert todo_res.status_code in (200, 201)
    assert todo_res.json()["title"] == "First test"
"""Local smoke test for the final production agent."""
from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    with TestClient(app) as client:
        print("health", client.get("/health").status_code)
        print("ready", client.get("/ready").status_code)

        no_auth = client.post("/ask", json={"user_id": "test", "question": "Hello"})
        print("noauth", no_auth.status_code)

        auth_headers = {"X-API-Key": "dev-key-change-me"}
        ask = client.post(
            "/ask",
            headers=auth_headers,
            json={"user_id": "test", "question": "What is Docker?"},
        )
        print("ask", ask.status_code, ask.json().get("storage"), ask.json().get("user_id"))

        session_id = ask.json()["session_id"]
        history = client.get(f"/sessions/{session_id}/history", headers=auth_headers)
        print("history", history.status_code)


if __name__ == "__main__":
    main()

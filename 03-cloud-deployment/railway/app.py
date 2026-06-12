"""
Agent Railway-ready.
Railway inject PORT env var tự động — agent phải dùng os.getenv("PORT").
"""
import os
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from utils.mock_llm import ask

app = FastAPI(title="Agent on Railway", version="1.0.0")
START_TIME = time.time()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "headline": "Welcome to the Cloud-Native AI Command Deck",
        "message": "Xin chào! Agent đã cất cánh trên Railway với phong cách hiện đại: nhanh, gọn, sẵn sàng scale.",
        "tagline": "From localhost to live cloud: one API, one container, one futuristic experience.",
        "experience": {
            "mode": "modern-tech",
            "vibe": "AI assistant + cloud platform + realtime operations",
            "promise": "Nhận câu hỏi, xử lý bằng agent, trả về phản hồi rõ ràng trong vài mili-giây.",
        },
        "stack": ["FastAPI", "Railway", "Docker-ready", "Mock LLM", "Health checks"],
        "try_it": {
            "docs": "/docs",
            "health": "/health",
            "ask": {
                "method": "POST",
                "path": "/ask",
                "body": {"question": "Tell me why cloud deployment feels futuristic"},
            },
        },
        "status": "online",
        "signature": "Lab 12 Deployment - modern cloud edition",
    }


@app.post("/ask")
async def ask_agent(request: Request):
    body = await request.json()
    question = body.get("question", "")
    if not question:
        raise HTTPException(422, "question required")
    answer = ask(question)
    return {
        "question": question,
        "answer": answer,
        "welcome": "Bạn đang nói chuyện với một AI agent chạy trên cloud - đây là bản demo deployment mang chất công nghệ hiện đại.",
        "modern_signal": {
            "latency_mindset": "low-latency API",
            "deployment_mindset": "cloud-native",
            "scaling_mindset": "stateless-ready",
        },
        "platform": "Railway",
        "served_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health():
    """
    Railway sẽ check endpoint này định kỳ.
    Trả về 200 = healthy. Non-200 = Railway restart container.
    """
    return {
        "status": "ok",
        "message": "Cloud agent is awake, responsive, and ready for modern AI traffic.",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "platform": "Railway",
        "runtime": "FastAPI on Railway",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    # ✅ Railway inject PORT — PHẢI đọc từ env
    port = int(os.getenv("PORT", 8000))
    print(f"Starting on port {port} (from PORT env var)")
    uvicorn.run(app, host="0.0.0.0", port=port)

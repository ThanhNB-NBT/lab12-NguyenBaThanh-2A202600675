# Day 12 Lab - Mission Answers

> **Student Name:** Nguyễn Bá Thành   
> **Student ID:** 2A202600675  
> **Date:** 12/06/2026

---

##  Submission Requirements

Submit a **GitHub repository** containing: https://github.com/ThanhNB-NBT/lab12-NguyenBaThanh-2A202600675.git

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. Secret/API key de trong code thay vi doc tu environment variable.
2. Port bi hardcode, kho deploy len Railway/Render vi cloud tu cap bien `PORT`.
3. Debug/reload phu hop localhost nhung khong nen bat trong production.
4. Khong co `/health` va `/ready`, nen platform khong biet app song hay san sang nhan traffic.
5. Khong co graceful shutdown, request dang chay co the bi cat ngang khi container bi stop.
6. Logging dang `print()` tu do, kho search va kho gom log tren cloud.
7. State luu trong memory, khi scale nhieu instance se mat context hoac rate limit khong dong nhat.

### Exercise 1.3: Comparison table

| Feature | Develop | Production | Why Important? |
|---|---|---|---|
| Config | Hardcode trong code | Doc tu environment variables | De deploy tren nhieu moi truong ma khong sua code |
| Secrets | Co nguy co commit vao git | Nam trong `.env`/cloud secret manager | Giam nguy co lo API key |
| Port | Co dinh `8000` | Doc tu `PORT` | Railway/Render/Cloud Run thuong inject port rieng |
| Health check | Khong co | Co `/health` va `/ready` | Cloud co the restart hoac route traffic dung luc |
| Logging | `print()` | JSON structured logging | De debug va quan sat production tot hon |
| Shutdown | Tat dot ngot | Xu ly `SIGTERM`/lifespan | Hoan tat request truoc khi container dung |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. Base image: `python:3.11-slim`.
2. Working directory: `/app` trong runtime image, `/build` trong builder stage.
3. COPY `requirements.txt` truoc de Docker cache layer cai dependency; khi chi sua source code thi khong can cai lai package.
4. `CMD` la lenh mac dinh co the override khi `docker run`; `ENTRYPOINT` la executable chinh, thuong kho override hon va dung khi image gan voi mot command co dinh.

### Exercise 2.3: Image size comparison

- Develop: `1.66GB` voi image `lab12-agent:develop`.
- Production/final: `247MB` voi image `lab12-agent:final`.
- Difference: final image nho hon khoang `85%` va dat yeu cau lab `< 500MB`; multi-stage chi copy runtime dependency va app, khong giu build context thua.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- URL: https://prolific-youth-production-7052.up.railway.app/
- Repo da co cau hinh san: `06-lab-complete/railway.toml` va `06-lab-complete/render.yaml`.
- Lenh deploy Railway:

```bash
cd 06-lab-complete
railway init
railway variables set AGENT_API_KEY=your-secret-key
railway variables set JWT_SECRET=your-jwt-secret
railway variables set MONTHLY_BUDGET_USD=10
railway variables set RATE_LIMIT_PER_MINUTE=10
railway up
railway domain
```

## Part 4: API Security

### Exercise 4.1-4.3: Test results

Local smoke test:

```text
health 200
ready 200
noauth 401
ask 200 memory test
history 200
```

Docker smoke test:

```text
GET /health -> 200
POST /ask without X-API-Key -> 401
POST /ask with X-API-Key -> 200
Docker image status -> healthy
Image size -> 247MB
```

### Exercise 4.4: Cost guard implementation

Cost guard nam trong `06-lab-complete/app/cost_guard.py`.

- Moi request uoc tinh token input/output bang so tu trong cau hoi/cau tra loi.
- Chi phi duoc tinh theo bang gia mock: input `$0.00015/1K tokens`, output `$0.00060/1K tokens`.
- Gioi han mac dinh la `$10/month`, doc tu `MONTHLY_BUDGET_USD`.
- Neu co `REDIS_URL`, usage duoc luu vao Redis key theo thang: `cost:YYYY-MM:global`.
- Neu khong co Redis local, app fallback memory de van test offline duoc.
- Khi vuot budget, API tra `402 Monthly budget exceeded`.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

- Health check: `GET /health` tra status, version, environment, uptime, request count va state store.
- Readiness check: `GET /ready` kiem tra app da startup va state store san sang.
- Graceful shutdown: FastAPI lifespan dat `_is_ready=False` khi shutdown, dong thoi co handler `SIGTERM` de log tin hieu stop tu container.
- Stateless design: session history, rate limit va cost guard deu co Redis-backed implementation; fallback memory chi dung cho local/offline.
- Rate limiting: sliding window 60 giay, mac dinh `10 req/min`, bucket theo `user_id` va API key.
- Load balancing: khi chay nhieu container, Redis giu state chung nen request di vao instance nao van doc duoc session/usage/rate limit.

## Part 6: Final Project

Final project nam trong `06-lab-complete/`.

Da hoan thanh:

- REST API `/ask`
- Conversation history qua `/sessions/{session_id}/history`
- Multi-stage Dockerfile
- Environment-based config
- API key authentication
- Rate limiting 10 req/min
- Cost guard `$10/month`
- Health/readiness checks
- Graceful shutdown
- Redis-backed stateless state
- JSON structured logging
- Railway/Render config

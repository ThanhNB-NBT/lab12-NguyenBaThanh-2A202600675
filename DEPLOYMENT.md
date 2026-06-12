# Deployment Information

## Public URL

Pending real cloud deployment. Replace this line after running Railway or Render:

```text
https://your-agent.railway.app
```

## Platform

Prepared for Railway and Render.

- Railway config: `06-lab-complete/railway.toml`
- Render config: `06-lab-complete/render.yaml`

## Local Validation

```text
Production readiness: 20/20 checks passed
Docker image: lab12-agent:final
Docker image size: 247MB
Container health: healthy
GET /health: 200
POST /ask without X-API-Key: 401
POST /ask with X-API-Key: 200
```

## Test Commands

### Health Check

```bash
curl https://your-agent.railway.app/health
# Expected: {"status":"ok", ...}
```

### API Test (with authentication)

```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"Hello"}'
```

### Local Docker Test

```bash
cd 06-lab-complete
docker build -t lab12-agent:final .
docker run --rm -p 8000:8000 -e AGENT_API_KEY=dev-key-change-me lab12-agent:final
curl http://localhost:8000/health
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: dev-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"What is Docker?"}'
```

## Environment Variables Set

- `PORT`
- `REDIS_URL`
- `AGENT_API_KEY`
- `JWT_SECRET`
- `LOG_LEVEL`
- `RATE_LIMIT_PER_MINUTE`
- `MONTHLY_BUDGET_USD`
- `SESSION_TTL_SECONDS`
- `ALLOWED_ORIGINS`

## Screenshots

Add screenshots after real deployment:

- Deployment dashboard: `screenshots/dashboard.png`
- Service running: `screenshots/running.png`
- Test results: `screenshots/test.png`

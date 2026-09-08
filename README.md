# Production GenAI API

A production-oriented Generative AI API built with **FastAPI, OpenAI, Docker, authentication, guardrails, rate limiting, automated tests, Prometheus, and Grafana**.

This project is being developed as a practical reference for building, securing, monitoring, containerizing, and eventually deploying a GenAI application to Azure.

> **Project status:** Core API, security baseline, Docker hardening, Prometheus, and Grafana monitoring are implemented. CI/CD and Azure deployment are planned next.

---

## Architecture

```text
                         Client
                           |
                           v
                 +---------------------+
                 |     FastAPI API     |
                 |                     |
                 | Authentication      |
                 | Guardrails          |
                 | Rate Limiting       |
                 | Request IDs         |
                 +----------+----------+
                            |
                            v
                 +---------------------+
                 |     LLM Service      |
                 |       OpenAI         |
                 +----------+----------+
                            |
                            v
                       LLM Response

Monitoring:

FastAPI /metrics --> Prometheus --> Grafana

Planned production path:

Client --> Azure Gateway --> FastAPI --> OpenAI
                         |
                         +--> Azure Monitor / Application Insights
```

---

## Features

### API

- FastAPI REST API
- `/generate` endpoint for LLM responses
- `/health` health endpoint
- `/metrics` Prometheus metrics endpoint
- Pydantic request/response validation
- Centralized application-specific exceptions

### GenAI

- OpenAI Responses API
- `gpt-5-mini` model
- Configurable OpenAI API key through environment variables
- OpenAI client timeout and retry configuration

### Security

- Bearer-token authentication
- Authorization dependency for admin-only endpoints
- Environment-based secrets
- Input validation and prompt guardrails
- Request size/length protection
- Docker runs as a non-root user
- Docker Linux capabilities dropped
- `no-new-privileges` enabled
- Read-only container filesystem
- `.env` excluded from Docker build context and Git

### Guardrails

The application blocks known unsafe instruction patterns such as attempts to:

- Ignore previous instructions
- Reveal the system prompt
- Bypass safety controls

Guardrails are implemented before the prompt is sent to the LLM.

> These rules are a baseline demonstration, not a complete enterprise prompt-injection defense. A production implementation should use layered controls and model/provider safety mechanisms.

### Rate limiting

- `slowapi` based request limiting
- `/generate` limited to `10 requests/minute`
- HTTP `429` returned when the limit is exceeded

> For multi-instance production deployment, a shared/distributed rate-limit store such as Redis should be used instead of an in-memory limiter.

### Observability

Prometheus metrics include:

- HTTP request count
- HTTP request latency
- LLM request count
- LLM request latency
- LLM input tokens
- LLM output tokens
- Python/process runtime metrics

Grafana is configured as the visualization layer over Prometheus.

### Testing

Automated tests cover authentication, authorization, rate limiting, and API behavior.

Current test baseline:

```text
19 passed
```

---

## Project Structure

```text
production-ai-training/
|
├── app/
│   ├── api.py
│   ├── auth.py
│   ├── config.py
│   ├── exceptions.py
│   ├── guardrails.py
│   ├── llm_service.py
│   ├── logging_config.py
│   └── metrics.py
│
├── tests/
│   └── ...
│
├── monitoring/
│   └── prometheus.yml
│
├── evaluation/
│   └── ...
│
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Local Development

### Prerequisites

- Python 3.13+
- Docker Desktop
- Git
- OpenAI API key

### Create virtual environment

```bash
python -m venv .venv
```

Activate it in Git Bash:

```bash
source .venv/Scripts/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
API_AUTH_TOKEN=your_api_auth_token
```

Never commit `.env` or expose secrets in source code.

A secure token can be generated with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Run the API Locally

From the project root:

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

API:

```text
http://localhost:8000
```

Health check:

```text
GET /health
```

Metrics:

```text
GET /metrics
```

---

## Generate an AI Response

The `/generate` endpoint requires a bearer token.

Example:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_AUTH_TOKEN" \
  -d '{"prompt":"Explain RAG in one sentence."}'
```

Example response:

```json
{
  "response": "RAG combines retrieval of relevant external information with generation by an LLM."
}
```

---

## Authentication and Authorization

Authentication currently uses a bearer token configured through `API_AUTH_TOKEN`.

Conceptually:

```text
Authentication = Who are you?
Authorization  = What are you allowed to do?
```

Expected HTTP behavior:

- `401 Unauthorized` → missing or invalid authentication
- `403 Forbidden` → authenticated but insufficient authorization

The current admin authorization implementation is intentionally a learning-stage baseline. A future production version will use proper identity claims/roles, such as JWT validation and Azure Entra ID.

---

## Docker

### Build image

```bash
docker build -t production-genai-api .
```

### Run hardened container

```bash
docker run -d \
  --name production-genai-api-container \
  -p 8000:8000 \
  --env-file .env \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges:true \
  production-genai-api
```

### Check container

```bash
docker ps
```

The image uses a non-root application user and includes a Docker health check against `/health`.

---

## Prometheus Monitoring

Prometheus is configured in:

```text
monitoring/prometheus.yml
```

The configuration scrapes:

```text
http://host.docker.internal:8000/metrics
```

### Start Prometheus

From the `monitoring` directory on the Windows/Git Bash development setup:

```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v "C:/Users/Vijay/OneDrive/Desktop/AI-Engineering/production-ai-training/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml" \
  prom/prometheus
```

Prometheus UI:

```text
http://localhost:9090
```

Target status:

```text
http://localhost:9090/targets
```

The production GenAI API target should report `UP`.

Example PromQL queries:

```promql
llm_requests_total
```

```promql
llm_input_tokens_total
```

```promql
llm_output_tokens_total
```

Average observed LLM latency for the current metric set:

```promql
llm_request_duration_seconds_sum
/
llm_request_duration_seconds_count
```

For production dashboards with enough traffic, percentile latency can be calculated from the histogram, for example P95:

```promql
histogram_quantile(
  0.95,
  rate(llm_request_duration_seconds_bucket[5m])
)
```

---

## Grafana

Grafana is used to visualize Prometheus metrics.

Start Grafana:

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

Grafana UI:

```text
http://localhost:3000
```

Configure Prometheus as a Grafana data source using:

```text
http://host.docker.internal:9090
```

Current dashboard metrics include:

- Total LLM Requests
- LLM Request Latency
- Total LLM Input Tokens
- Total LLM Output Tokens

Planned dashboard additions include API error rate, request rate, availability, and alerting.

---

## Metrics Design

Request IDs are intentionally **not** used as Prometheus labels because request IDs have high cardinality and can create unnecessary metric-series growth.

Request IDs belong in logs/traces, while Prometheus is used for aggregate operational metrics.

Example:

```text
Logs/Traces:
request_id=abc123

Prometheus:
http_requests_total{method="POST",endpoint="/generate",status="200"}
```

This separation is important for scalable observability.

---

## Error Handling

Application-specific exceptions include:

- `ApplicationError`
- `ConfigurationError`
- `LLMServiceError`
- `GuardrailError`

The API maps failures to appropriate HTTP responses, including:

- `400` for blocked/invalid guarded input
- `401` for authentication failures
- `403` for authorization failures
- `429` for rate-limit violations
- `503` for LLM service failures
- `500` for configuration failures

---

## Production Considerations

The current project is intentionally built in layers. The following production concerns are identified but are not all fully implemented yet:

### Planned

- JWT-based authentication
- Azure Entra ID integration
- Real role/claim-based authorization
- Distributed rate limiting with Redis/Azure Cache for Redis
- Centralized logs
- Alerting
- Azure Monitor / Application Insights
- CI/CD pipeline
- Container registry integration
- Azure deployment
- Production secret management with Azure Key Vault
- HTTPS/TLS termination through an appropriate Azure ingress/gateway
- Autoscaling
- Network isolation/private connectivity where required
- Reliability and disaster-recovery controls

---

## Security Principles

This project follows several important production security principles:

1. Never hard-code secrets.
2. Keep secrets outside Git.
3. Validate untrusted input.
4. Authenticate protected endpoints.
5. Authorize privileged operations.
6. Rate-limit expensive AI operations.
7. Run containers as non-root.
8. Drop unnecessary Linux capabilities.
9. Prevent privilege escalation.
10. Prefer read-only container filesystems where possible.
11. Avoid high-cardinality Prometheus labels.
12. Do not log secrets or sensitive prompt content unnecessarily.
13. Treat prompt injection and data leakage as GenAI-specific security risks.

---

## Testing

Run the automated test suite with:

```bash
pytest -q
```

Current baseline:

```text
19 passed
```

Tests should be run before building or deploying the application.

---

## Roadmap

```text
[✓] FastAPI GenAI API
[✓] OpenAI integration
[✓] Configuration management
[✓] Error handling
[✓] Guardrails
[✓] Structured logging
[✓] Request IDs
[✓] Health checks
[✓] Automated tests
[✓] Docker containerization
[✓] Docker runtime hardening
[✓] Authentication
[✓] Authorization baseline
[✓] Rate limiting
[✓] Prometheus metrics
[✓] Grafana integration
[ ] Production alerting
[ ] CI/CD
[ ] Azure Container Registry
[ ] Azure deployment
[ ] Azure Monitor / Application Insights
[ ] Azure Key Vault
[ ] Production identity with Entra ID
[ ] Distributed rate limiting
[ ] Production scaling and resilience
```

---

## Learning Goals

This project is designed to demonstrate practical AI engineering beyond simply calling an LLM API.

The target production lifecycle is:

```text
Build
  ↓
Test
  ↓
Secure
  ↓
Containerize
  ↓
Instrument
  ↓
Monitor
  ↓
Automate with CI/CD
  ↓
Deploy to Azure
  ↓
Operate and optimize
```

The same engineering principles can later be extended to RAG, multimodal RAG, agentic AI, evaluation pipelines, and other enterprise GenAI systems.

---

## License

This project is currently intended as a learning and portfolio project.

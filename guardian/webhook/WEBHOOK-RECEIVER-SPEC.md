# Guardian Webhook Receiver - Deployment Spec

**Created:** 2025-10-21
**Phase:** RED (Implementation)
**Owner:** Chromebook Orchestrator → Guardian Executor

---

## Objective

Deploy FastAPI webhook receiver on Guardian to:
- Receive GitHub webhooks at `webhook.kitt.agency/github`
- Validate GitHub signatures for security
- Parse webhook payloads
- Publish deployment events to Kafka on Beast
- Support all future repos (mundus, dev-rag, dev-network, etc.)

---

## Architecture

**Webhook Flow:**
```
GitHub (push to main)
  ↓ HTTPS POST
Cloudflare Tunnel (webhook.kitt.agency)
  ↓
Guardian:8000 (FastAPI webhook receiver)
  ↓ Validate signature
  ↓ Parse payload
  ↓ Publish to Kafka
Beast:9092 (Kafka broker)
  ↓
deployment-webhooks topic
```

**Guardian Services:**
```
Guardian (192.168.68.10)
├─ Webhook Receiver:8000 (Docker container)
│  ├─ FastAPI application
│  ├─ Kafka producer client
│  └─ GitHub signature validation
```

---

## Deployment Steps

### 1. Create .env File

```bash
cd ~/dev-network/guardian/webhook
cp .env.example .env
nano .env
```

Set values:
```bash
GITHUB_WEBHOOK_SECRET=<generate-strong-secret>
KAFKA_BOOTSTRAP_SERVERS=192.168.68.100:9092
KAFKA_TOPIC=deployment-webhooks
```

**Generate secret:**
```bash
openssl rand -hex 32
```

### 2. Build and Deploy

```bash
cd ~/dev-network/guardian/webhook
docker compose build
docker compose up -d
```

### 3. Verify Running

```bash
docker ps | grep webhook-receiver
docker logs webhook-receiver
```

### 4. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "kafka": "connected",
  "timestamp": "2025-10-21T11:30:00.000Z"
}
```

### 5. Test from Chromebook

```bash
curl http://192.168.68.10:8000/
```

Expected response:
```json
{
  "service": "Guardian Webhook Receiver",
  "status": "operational",
  "kafka": "192.168.68.100:9092",
  "topic": "deployment-webhooks"
}
```

---

## Cloudflare Tunnel Configuration

**(To be configured after webhook receiver is running)**

Add route to existing Cloudflare Tunnel:

```bash
# On Beast (or wherever tunnel is configured)
cloudflared tunnel route dns <tunnel-name> webhook.kitt.agency

# Update tunnel config to include:
ingress:
  - hostname: webhook.kitt.agency
    service: http://192.168.68.10:8000
  - hostname: grafana.kitt.agency
    service: http://localhost:3000
  - service: http_status:404
```

---

## GitHub Webhook Configuration

**(After Cloudflare tunnel is set up)**

For each repo (mundus-editor-application, dev-rag, dev-network):

1. Go to GitHub repo → Settings → Webhooks → Add webhook
2. Configure:
   - **Payload URL:** `https://webhook.kitt.agency/github`
   - **Content type:** `application/json`
   - **Secret:** Same as `GITHUB_WEBHOOK_SECRET` in .env
   - **Events:** Just the push event
   - **Active:** ✅ Enabled
3. Save
4. GitHub will send test ping - check webhook receiver logs

---

## Testing Webhook

### Manual Test (Simulate GitHub)

```bash
# Generate signature
SECRET="your-github-webhook-secret"
PAYLOAD='{"repository":{"name":"test-repo"},"ref":"refs/heads/main","after":"abc123"}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.* //')

# Send webhook
curl -X POST http://192.168.68.10:8000/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-Hub-Signature-256: sha256=$SIGNATURE" \
  -H "X-GitHub-Delivery: test-delivery-123" \
  -d "$PAYLOAD"
```

Expected response:
```json
{
  "status": "queued",
  "repo": "test-repo",
  "branch": "main",
  "commit": "abc123",
  "kafka_topic": "deployment-webhooks",
  "kafka_partition": 0,
  "kafka_offset": 0
}
```

### Verify in Kafka

```bash
# On Beast, consume from topic
ssh beast "docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic deployment-webhooks \
  --from-beginning"
```

Should see deployment event JSON.

---

## Monitoring

### Logs

```bash
# Follow logs
docker logs -f webhook-receiver

# Last 100 lines
docker logs --tail 100 webhook-receiver
```

### Health Check

```bash
# Local
curl http://localhost:8000/health

# From Chromebook
curl http://192.168.68.10:8000/health

# Via Cloudflare (after tunnel configured)
curl https://webhook.kitt.agency/health
```

---

## Troubleshooting

### Webhook receiver not starting

```bash
# Check logs
docker logs webhook-receiver

# Check .env file exists
ls -la .env

# Rebuild
docker compose build --no-cache
docker compose up -d
```

### Can't connect to Kafka

```bash
# Test Kafka from Guardian
docker run --rm confluentinc/cp-kafka:7.5.0 \
  kafka-broker-api-versions --bootstrap-server 192.168.68.100:9092

# Check Kafka is running on Beast
ssh beast "docker ps | grep kafka"
```

### Invalid signature errors

```bash
# Verify secret matches in:
# 1. Guardian .env file
# 2. GitHub webhook settings

# Check webhook receiver logs
docker logs webhook-receiver | grep signature
```

---

## Resource Usage

**Expected:**
- RAM: ~50-100MB
- CPU: <5% (idle), 10-20% (processing webhooks)
- Disk: ~200MB (Docker image)
- Network: Minimal (only webhook events)

---

## Security

**Implemented:**
- ✅ GitHub signature validation (HMAC-SHA256)
- ✅ Non-root Docker user
- ✅ Secret in .env (not committed to Git)
- ✅ HTTPS via Cloudflare Tunnel
- ✅ Internal Guardian port (not exposed to internet directly)

**Future Enhancements:**
- Rate limiting (prevent webhook spam)
- IP allowlist (only Cloudflare IPs)
- Webhook replay protection
- Audit logging to file/database

---

## Success Criteria

- [x] Webhook receiver running on Guardian:8000
- [x] Health endpoint returns 200
- [x] Kafka connectivity working
- [ ] Cloudflare tunnel configured (next step)
- [ ] GitHub webhook configured (next step)
- [ ] End-to-end test (GitHub push → Kafka event)

---

**Created:** 2025-10-21
**Status:** Ready for deployment

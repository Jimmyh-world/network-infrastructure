# Webhook Auto-Deployment System - Operations Guide

**Created:** 2025-10-21
**System:** GitOps webhook-based auto-deployment
**Status:** Production operational

---

## 🎯 How the System Works

### Automatic Deployment Flow

**When you push code to GitHub:**

```
1. You: git push origin main
   ↓
2. GitHub: Sends webhook POST to webhook.kitt.agency/github
   ↓
3. Cloudflare Tunnel: Routes to Guardian:8000
   ↓
4. Guardian: Validates signature, publishes to Kafka
   ↓
5. Kafka: Queues deployment event (deployment-webhooks topic)
   ↓
6. Beast Worker: Consumes event, executes deployment
   ↓
7. Deployment: git pull + docker compose up -d --build
   ↓
8. Result: Published to Kafka (deployment-results topic)
   ↓
9. Services: Auto-updated (3-7 seconds total)
```

**No manual intervention needed!** 🚀

---

## 📋 Using the System

### How to Deploy Code

**Method 1: Push to main (Recommended)**

```bash
# Make your changes
git add .
git commit -m "feat: Add new feature"
git push origin main

# That's it! Deployment happens automatically within 5-10 seconds
```

**Method 2: Merge Pull Request**

```bash
# Create PR, review, approve, merge to main
# Deployment triggers automatically on merge
```

### How to Verify Deployment

**Check deployment status:**

```bash
# Method 1: GitHub webhook deliveries
gh api repos/ydun-code-library/Mundus-editor-application/hooks/576484443/deliveries \
  | jq '.[0] | {delivered_at, status: .status_code, event}'

# Method 2: Kafka deployment results
ssh beast "docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic deployment-results \
  --from-beginning --timeout-ms 5000 2>/dev/null \
  | jq 'select(.repo_name == \"Mundus-editor-application\") | {commit: .commit, success, message}' \
  | tail -5"

# Method 3: Beast worker logs
ssh beast "tail -30 ~/deployment-worker.log | grep -E '(Deployment|✅|❌)'"

# Method 4: Check service is updated
ssh beast "docker ps | grep mundus"
ssh beast "cd ~/Mundus-editor-application && git log -1 --oneline"
```

---

## 🔧 System Operations

### Start/Stop Components

**Guardian Webhook Receiver:**
```bash
# Start
ssh guardian "cd ~/dev-network/guardian/webhook && docker compose up -d"

# Stop
ssh guardian "cd ~/dev-network/guardian/webhook && docker compose down"

# Restart
ssh guardian "cd ~/dev-network/guardian/webhook && docker compose restart"

# Logs
ssh guardian "docker logs -f webhook-receiver"
```

**Beast Deployment Worker:**
```bash
# Start
ssh beast "cd ~/dev-network/beast/deployment-worker && \
  nohup python3 deployment_worker.py > ~/deployment-worker-console.log 2>&1 &"

# Stop
ssh beast "pkill -f deployment_worker.py"

# Restart
ssh beast "pkill -f deployment_worker.py && sleep 2 && \
  cd ~/dev-network/beast/deployment-worker && \
  nohup python3 deployment_worker.py > ~/deployment-worker-console.log 2>&1 &"

# Logs
ssh beast "tail -f ~/deployment-worker.log"
```

**Kafka:**
```bash
# Start
ssh beast "cd ~/dev-network/beast/kafka && docker compose up -d"

# Stop
ssh beast "cd ~/dev-network/beast/kafka && docker compose down"

# Restart
ssh beast "cd ~/dev-network/beast/kafka && docker compose restart"

# Logs
ssh beast "docker logs -f kafka"
```

**Cloudflare Tunnel:**
```bash
# Start
ssh beast "cd ~/dev-network/beast && \
  nohup cloudflared tunnel --config cloudflare/config.yml run > ~/cloudflared-tunnel.log 2>&1 &"

# Stop
ssh beast "pkill cloudflared"

# Restart
ssh beast "pkill cloudflared && sleep 2 && \
  cd ~/dev-network/beast && \
  nohup cloudflared tunnel --config cloudflare/config.yml run > ~/cloudflared-tunnel.log 2>&1 &"

# Logs
ssh beast "tail -f ~/cloudflared-tunnel.log"
```

---

## 🔍 Monitoring

### Health Checks

**Quick health check (all components):**
```bash
# Guardian webhook receiver
curl -s https://webhook.kitt.agency/health | jq .

# Kafka broker
ssh beast "docker ps | grep kafka"

# Deployment worker
ssh beast "ps aux | grep deployment_worker | grep -v grep"

# Cloudflare Tunnel
curl -s -o /dev/null -w "%{http_code}\n" https://webhook.kitt.agency/health
# Should return: 200
```

### View Deployment History

**All deployments:**
```bash
ssh beast "docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic deployment-results \
  --from-beginning --timeout-ms 5000 2>/dev/null \
  | jq '{repo: .repo_name, commit: .commit[:7], success, timestamp: .result_timestamp}'"
```

**Successful only:**
```bash
ssh beast "docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic deployment-results \
  --from-beginning --timeout-ms 5000 2>/dev/null \
  | jq 'select(.success == true) | {repo: .repo_name, commit: .commit[:7], timestamp: .result_timestamp}'"
```

**Failed only:**
```bash
ssh beast "docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic deployment-results \
  --from-beginning --timeout-ms 5000 2>/dev/null \
  | jq 'select(.success == false) | {repo: .repo_name, error: .message, details}'"
```

### Kafka UI Dashboard

**Access:** http://192.168.68.100:8082

**Features:**
- View all topics
- Inspect messages
- Monitor consumer groups
- Check broker health
- View deployment events and results

---

## 🔧 Troubleshooting

### Webhook not received by Guardian

**Check:**
```bash
# 1. Cloudflare Tunnel running
ssh beast "ps aux | grep cloudflared | grep -v grep"

# 2. Guardian webhook receiver running
ssh guardian "docker ps | grep webhook-receiver"

# 3. Test endpoint
curl https://webhook.kitt.agency/health
```

**Fix:**
```bash
# Restart Cloudflare Tunnel
ssh beast "pkill cloudflared && \
  cd ~/dev-network/beast && \
  nohup cloudflared tunnel --config cloudflare/config.yml run > ~/cloudflared-tunnel.log 2>&1 &"

# Restart Guardian webhook receiver
ssh guardian "cd ~/dev-network/guardian/webhook && docker compose restart"
```

### Deployment not executing

**Check:**
```bash
# 1. Worker running
ssh beast "ps aux | grep deployment_worker | grep -v grep"

# 2. Kafka connectivity
ssh beast "docker exec kafka kafka-topics --list --bootstrap-server localhost:9092"

# 3. Consumer group
ssh beast "docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group deployment-worker"
```

**Fix:**
```bash
# Restart worker
ssh beast "pkill -f deployment_worker && \
  cd ~/dev-network/beast/deployment-worker && \
  nohup python3 deployment_worker.py > ~/deployment-worker-console.log 2>&1 &"
```

### Git pull failures

**Check:**
```bash
# Verify repo exists
ssh beast "ls -la ~/Mundus-editor-application"

# Test git pull manually
ssh beast "cd ~/Mundus-editor-application && git pull origin main"

# Check SSH keys
ssh beast "ssh -T git@github.com"
```

### Docker compose failures

**Check:**
```bash
# Verify docker-compose.yml exists
ssh beast "ls -la ~/dev-network/beast/docker/mundus/docker-compose.yml"

# Test manually
ssh beast "cd ~/dev-network/beast/docker/mundus && docker compose up -d --build"

# Check Docker daemon
ssh beast "docker ps"
```

---

## 📊 Monitoring Dashboard (Kafka UI)

**Access:** http://192.168.68.100:8082

### Key Metrics to Watch

**Topics:**
- `deployment-webhooks` - Should show recent messages when you push
- `deployment-results` - Should show deployment success/failure

**Consumer Groups:**
- `deployment-worker` - Should show 0 lag (no backlog)

**Brokers:**
- Should show 1 broker healthy

---

## 🎓 Key Learnings

### How Webhooks Work

**GitHub → Guardian:**
- GitHub sends POST request to webhook.kitt.agency/github
- Includes signature header: `X-Hub-Signature-256: sha256=...`
- Guardian validates signature using shared secret
- If valid: publishes to Kafka
- If invalid: rejects with 401

### How Kafka Works

**Guardian → Kafka → Beast:**
- Guardian publishes message to `deployment-webhooks` topic
- Message includes: repo name, branch, commit, timestamp
- Beast worker subscribes to topic (consumer group)
- Worker processes messages in order per partition
- Worker publishes result to `deployment-results` topic

### How Deployment Works

**Beast Worker Execution:**
1. Receives event from Kafka
2. Looks up repo configuration
3. Executes: `cd ~/repo && git pull origin main`
4. Executes: `cd ~/compose-path && docker compose up -d --build`
5. Publishes result (success/failure) to Kafka

---

**Created:** 2025-10-21
**Status:** Production operational ✅
**Documentation:** Complete usage and troubleshooting guide

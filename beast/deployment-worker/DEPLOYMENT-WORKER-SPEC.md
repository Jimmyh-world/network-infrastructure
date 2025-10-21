# Beast Deployment Worker - Deployment Spec

**Created:** 2025-10-21
**Phase:** RED Phase 3 (Implementation)
**Owner:** Chromebook Orchestrator → Beast Executor

---

## Objective

Deploy Kafka consumer on Beast to:
- Poll `deployment-webhooks` topic for GitHub push events
- Execute git pull + docker compose for affected repositories
- Report deployment results to `deployment-results` topic
- Support multiple repositories (mundus, dev-network, dev-rag, etc.)

---

## Architecture

**Deployment Flow:**
```
Kafka Topic: deployment-webhooks
  ↓
Beast Deployment Worker (Python Kafka consumer)
  ↓ Read deployment event
  ↓ Identify repository
  ↓
Execute deployment:
  1. cd /home/jimmyb/<repo>
  2. git pull origin main
  3. docker compose up -d --build (if configured)
  ↓
Report result to Kafka
  ↓
Kafka Topic: deployment-results
```

---

## Repository Configurations

### Supported Repositories

**1. mundus-editor-application**
```python
{
    'path': '/home/jimmyb/mundus-editor-application',
    'compose_path': '/home/jimmyb/mundus-editor-application',
    'compose_file': 'docker-compose.yml',
    'enabled': True
}
```

**Deployment steps:**
1. `cd /home/jimmyb/mundus-editor-application`
2. `git pull origin main`
3. `docker compose up -d --build`

**2. dev-network (network-infrastructure)**
```python
{
    'path': '/home/jimmyb/dev-network',
    'compose_path': '/home/jimmyb/dev-network/beast/docker',
    'compose_file': 'docker-compose.yml',
    'enabled': True
}
```

**Deployment steps:**
1. `cd /home/jimmyb/dev-network`
2. `git pull origin main`
3. `cd /home/jimmyb/dev-network/beast/docker`
4. `docker compose up -d --build`

**3. dev-rag**
```python
{
    'path': '/home/jimmyb/dev-rag',
    'compose_path': None,
    'enabled': False  # Not yet implemented
}
```

**Status:** Disabled (no Docker compose yet)

---

## Implementation Steps

### 1. Install Dependencies

```bash
cd ~/dev-network/beast/deployment-worker
pip3 install -r requirements.txt
```

**Dependencies:**
- `kafka-python==2.0.2` - Kafka consumer client

### 2. Create Log Directory

```bash
sudo touch /var/log/deployment-worker.log
sudo chown jimmyb:jimmyb /var/log/deployment-worker.log
```

### 3. Install Systemd Service

```bash
sudo cp deployment-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable deployment-worker
sudo systemctl start deployment-worker
```

### 4. Verify Running

```bash
sudo systemctl status deployment-worker
journalctl -u deployment-worker -f
```

---

## Kafka Consumer Configuration

**Consumer Group:** `deployment-worker`
- Benefit: Multiple workers can share the load (future scaling)
- Auto-commit: Enabled (every 1 second)
- Offset reset: Latest (don't replay old messages on startup)

**Input Topic:** `deployment-webhooks`
- Partition assignment: Automatic (Kafka assigns partitions)
- Deserialization: JSON

**Output Topic:** `deployment-results`
- Key: Repository name (ensures ordering per repo)
- Serialization: JSON
- Acks: All (guaranteed delivery)

---

## Deployment Event Schema

**Input (from deployment-webhooks topic):**
```json
{
  "event_type": "deployment",
  "repo_name": "mundus-editor-application",
  "repo_full_name": "Jimmyh-world/mundus-editor-application",
  "branch": "main",
  "commit": "abc123def456",
  "github_event": "push",
  "github_delivery_id": "12345-67890",
  "timestamp": "2025-10-21T11:19:37.121181",
  "triggered_by": "github-webhook"
}
```

**Output (to deployment-results topic):**
```json
{
  "event_type": "deployment_result",
  "repo_name": "mundus-editor-application",
  "repo_full_name": "Jimmyh-world/mundus-editor-application",
  "branch": "main",
  "commit": "abc123def456",
  "github_delivery_id": "12345-67890",
  "original_timestamp": "2025-10-21T11:19:37.121181",
  "result_timestamp": "2025-10-21T11:20:15.442298",
  "success": true,
  "message": "Successfully deployed mundus-editor-application (commit: abc123d)",
  "details": {
    "log": [
      {
        "step": "git_pull",
        "command": "git pull origin main",
        "success": true,
        "output": "Already up to date.",
        "error": ""
      },
      {
        "step": "docker_compose",
        "command": "docker compose -f docker-compose.yml up -d --build",
        "success": true,
        "output": "Container mundus-editor Recreated...",
        "error": ""
      }
    ],
    "commit": "abc123def456",
    "branch": "main"
  }
}
```

---

## Error Handling

### Git Pull Failures

**Scenarios:**
- Network error
- Merge conflicts
- Repository doesn't exist

**Handling:**
- Log error to `deployment-results` topic
- Set `success: false`
- Include full error message in `details.error`
- Worker continues (doesn't crash)

### Docker Compose Failures

**Scenarios:**
- Image build failed
- Container startup failed
- Port conflict
- Resource limits

**Handling:**
- Log error to `deployment-results` topic
- Set `success: false`
- Include docker compose output in `details.log`
- Previous containers may still be running

### Kafka Connection Failures

**Scenarios:**
- Kafka broker down
- Network partition

**Handling:**
- Automatic reconnection (built into kafka-python)
- Exponential backoff
- Systemd restarts worker if crashed

---

## Logging

**Log File:** `/var/log/deployment-worker.log`

**Log Format:**
```
2025-10-21 11:20:00,123 - __main__ - INFO - Received deployment event!
2025-10-21 11:20:00,124 - __main__ - INFO -   Repository: Jimmyh-world/mundus-editor-application
2025-10-21 11:20:00,125 - __main__ - INFO -   Branch: main
2025-10-21 11:20:00,126 - __main__ - INFO -   Commit: abc123d
2025-10-21 11:20:01,234 - __main__ - INFO - Executing: git pull origin main
2025-10-21 11:20:02,345 - __main__ - INFO - Executing: docker compose up -d --build
2025-10-21 11:20:15,456 - __main__ - INFO - ✅ Deployment SUCCESSFUL
```

**Journalctl:**
```bash
# Real-time logs
journalctl -u deployment-worker -f

# Last 100 lines
journalctl -u deployment-worker -n 100

# Errors only
journalctl -u deployment-worker -p err
```

---

## Monitoring

### Health Checks

**Process running:**
```bash
systemctl status deployment-worker
ps aux | grep deployment_worker
```

**Kafka connectivity:**
```bash
# Check consumer group
docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group deployment-worker
```

**Lag monitoring:**
- Lag = messages waiting to be consumed
- Expected: 0 (worker keeps up with events)
- Alert: If lag > 10 (worker falling behind)

### Metrics (Future Enhancement)

**Prometheus metrics to expose:**
- Deployments total (counter)
- Deployments successful (counter)
- Deployments failed (counter)
- Deployment duration (histogram)
- Kafka lag (gauge)

---

## Security

### Permissions

**Worker runs as:** `jimmyb` user (non-root)

**File permissions:**
- deployment_worker.py: 755 (executable)
- deployment-worker.log: 644 (writable by jimmyb)

**Docker access:**
- User `jimmyb` must be in `docker` group
- Verify: `groups jimmyb` (should include `docker`)

### Secrets

**None required** (all local operations)

**Future:** If deploying to external services, add environment secrets

---

## Testing

### Manual Test

**1. Publish test event to Kafka:**
```bash
cat <<EOF | docker exec -i kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic deployment-webhooks
{"event_type":"deployment","repo_name":"dev-network","repo_full_name":"Jimmyh-world/network-infrastructure","branch":"main","commit":"test123","github_event":"push","github_delivery_id":"test-456","timestamp":"2025-10-21T12:00:00","triggered_by":"manual-test"}
EOF
```

**2. Watch worker logs:**
```bash
journalctl -u deployment-worker -f
```

**3. Verify deployment executed:**
```bash
cd ~/dev-network && git log -1
docker ps
```

**4. Check result in Kafka:**
```bash
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic deployment-results \
  --from-beginning \
  --max-messages 1
```

---

## Troubleshooting

### Worker not starting

```bash
# Check status
sudo systemctl status deployment-worker

# Check logs
journalctl -u deployment-worker -n 50

# Verify Python dependencies
pip3 list | grep kafka

# Run manually (debug mode)
cd ~/dev-network/beast/deployment-worker
python3 deployment_worker.py
```

### Worker crashing

```bash
# Check crash logs
journalctl -u deployment-worker --since "10 minutes ago"

# Check Python errors
journalctl -u deployment-worker -p err

# Restart worker
sudo systemctl restart deployment-worker
```

### Deployments not executing

```bash
# Check worker is consuming messages
docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group deployment-worker

# Check Kafka connectivity from worker
journalctl -u deployment-worker | grep -i kafka

# Check repository paths exist
ls -la /home/jimmyb/mundus-editor-application
ls -la /home/jimmyb/dev-network
```

### Git pull failures

```bash
# Verify git works manually
cd /home/jimmyb/mundus-editor-application
git pull origin main

# Check SSH keys
ssh -T git@github.com

# Check worker has correct permissions
sudo -u jimmyb git pull origin main
```

---

## Success Criteria

- [x] Worker code created (deployment_worker.py)
- [x] Systemd service file created
- [x] Requirements.txt created
- [ ] Dependencies installed on Beast
- [ ] Systemd service enabled and started
- [ ] Worker consuming from deployment-webhooks topic
- [ ] Test deployment executes successfully
- [ ] Result published to deployment-results topic

---

**Created:** 2025-10-21
**Status:** Ready for deployment on Beast

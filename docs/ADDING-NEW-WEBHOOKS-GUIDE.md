# Adding New Repositories to Webhook Auto-Deployment

**Created:** 2025-10-21
**System:** GitOps webhook auto-deployment
**Audience:** Future you, when adding new repos

---

## 🎯 Quick Start: Add a New Repository

**Time:** ~10 minutes per repository

**Prerequisites:**
- Repository exists on GitHub
- Repository cloned on Beast
- Docker compose configured (or none needed)

---

## 📋 Step-by-Step Guide

### Step 1: Add Repository to Deployment Worker Config

**File:** `dev-network/beast/deployment-worker/deployment_worker.py`

**Edit the `REPO_CONFIGS` dictionary:**

```python
REPO_CONFIGS = {
    # ... existing repos ...

    'your-new-repo-name': {
        'path': '/home/jimmyb/your-new-repo-name',
        'compose_path': '/home/jimmyb/your-new-repo-name',  # Or wherever docker-compose.yml is
        'compose_file': 'docker-compose.yml',
        'enabled': True
    },
}
```

**Important:**
- `path`: Where to execute `git pull origin main`
- `compose_path`: Where docker-compose.yml is located
- `compose_file`: Name of compose file (usually `docker-compose.yml`)
- `enabled`: Set to `True` to activate

**Commit to GitHub:**
```bash
cd ~/dev-network
git add beast/deployment-worker/deployment_worker.py
git commit -m "feat: Add auto-deployment support for your-new-repo-name"
git push origin main
```

---

### Step 2: Deploy Updated Worker to Beast

**Pull latest config:**
```bash
ssh beast "cd ~/dev-network && git pull origin main"
```

**Restart deployment worker:**
```bash
ssh beast "pkill -f deployment_worker.py && sleep 2 && \
  cd ~/dev-network/beast/deployment-worker && \
  nohup python3 deployment_worker.py > ~/deployment-worker-console.log 2>&1 &"
```

**Verify worker started:**
```bash
ssh beast "tail -20 ~/deployment-worker.log | grep 'Connected to Kafka'"
# Should see: "Connected to Kafka successfully!"
```

---

### Step 3: Add GitHub Webhook to Repository

**Use GitHub CLI:**

```bash
gh api repos/YOUR-ORG/your-new-repo-name/hooks \
  --method POST \
  --field name=web \
  --field active=true \
  --field events[]=push \
  --field config[url]=https://webhook.kitt.agency/github \
  --field config[content_type]=json \
  --field config[secret]=0b263f5caf4c9d324c0a53c805a400681b0183a59d6a100ca64caf01d63e2e7d \
  --field config[insecure_ssl]=0
```

**Webhook Configuration:**
- **Payload URL:** `https://webhook.kitt.agency/github`
- **Content type:** `application/json`
- **Secret:** `0b263f5caf4c9d324c0a53c805a400681b0183a59d6a100ca64caf01d63e2e7d`
- **Events:** Push events only
- **Active:** Yes

**Verify webhook created:**
```bash
gh api repos/YOUR-ORG/your-new-repo-name/hooks \
  | jq '.[] | {id, url: .config.url, active, events}'
```

---

### Step 4: Test End-to-End

**Method 1: Trigger test webhook**
```bash
WEBHOOK_ID=$(gh api repos/YOUR-ORG/your-new-repo-name/hooks | jq '.[0].id')

gh api repos/YOUR-ORG/your-new-repo-name/hooks/$WEBHOOK_ID/tests \
  --method POST
```

**Method 2: Push empty commit**
```bash
cd ~/your-repo-local-path
git commit --allow-empty -m "test: Trigger auto-deployment"
git push origin main
```

**Verify deployment:**
```bash
# Check worker logs
ssh beast "tail -30 ~/deployment-worker.log"

# Should see:
# - Received deployment event for your-new-repo-name
# - Git pull executed
# - Docker compose executed (if configured)
# - ✅ Deployment SUCCESSFUL
```

---

## 📋 Repository Configuration Examples

### Example 1: Simple Repo (Just Git Pull)

**Use case:** Static site, no Docker compose

```python
'my-static-site': {
    'path': '/home/jimmyb/my-static-site',
    'compose_path': None,  # No Docker compose
    'enabled': True
}
```

**Deployment:**
- Git pull only
- No Docker compose
- Use for: docs sites, static HTML, etc.

---

### Example 2: Docker Compose at Root

**Use case:** App with docker-compose.yml in repo root

```python
'my-app': {
    'path': '/home/jimmyb/my-app',
    'compose_path': '/home/jimmyb/my-app',  # Same as path
    'compose_file': 'docker-compose.yml',
    'enabled': True
}
```

**Deployment:**
1. `cd ~/my-app && git pull origin main`
2. `cd ~/my-app && docker compose up -d --build`

---

### Example 3: Split Code and Deployment

**Use case:** Code in one repo, deployment config in another (like Mundus)

```python
'Mundus-editor-application': {
    'path': '/home/jimmyb/Mundus-editor-application',  # Code here
    'compose_path': '/home/jimmyb/dev-network/beast/docker/mundus',  # Compose here
    'compose_file': 'docker-compose.yml',
    'enabled': True
}
```

**Deployment:**
1. `cd ~/Mundus-editor-application && git pull origin main` (get latest code)
2. `cd ~/dev-network/beast/docker/mundus && docker compose up -d --build` (restart services)

**Use when:** Deployment config is infrastructure-specific, not in app repo

---

### Example 4: Custom Compose File Name

**Use case:** Using docker-compose.prod.yml or similar

```python
'my-prod-app': {
    'path': '/home/jimmyb/my-prod-app',
    'compose_path': '/home/jimmyb/my-prod-app',
    'compose_file': 'docker-compose.prod.yml',  # Custom filename
    'enabled': True
}
```

---

### Example 5: Disabled (Not Ready Yet)

**Use case:** Repo exists but not ready for auto-deployment

```python
'dev-rag': {
    'path': '/home/jimmyb/dev-rag',
    'compose_path': None,
    'enabled': False  # Disabled until Docker compose added
}
```

**To enable later:**
1. Add Docker compose to repo
2. Set `enabled: True`
3. Add `compose_path` and `compose_file`
4. Restart worker
5. Add GitHub webhook

---

## 🔄 Adding Different Types of Webhooks

### Current: GitHub Push Webhooks

**What's supported:**
- Push events to main/master branches only
- Auto-deployment via git pull + docker compose

**Signature:** HMAC-SHA256

---

### Future: GitHub Release Webhooks

**To add release-based deployments:**

**1. Modify Guardian webhook receiver** (`guardian/webhook/webhook_receiver.py`):

```python
elif x_github_event == 'release':
    release_event = {
        "event_type": "release",
        "repo_name": repo_name,
        "release_tag": payload.get('release', {}).get('tag_name'),
        # ... more fields
    }

    producer.send('deployment-webhooks', value=release_event)
```

**2. Update GitHub webhook** to include `release` event:
```bash
gh api repos/YOUR-ORG/your-repo/hooks/WEBHOOK_ID \
  --method PATCH \
  --field events[]=push \
  --field events[]=release
```

**3. Update Beast worker** to handle release events differently

---

### Future: Other Git Providers (GitLab, Bitbucket)

**To support GitLab webhooks:**

**1. Add new endpoint** in Guardian (`/gitlab`):
```python
@app.post("/gitlab")
async def gitlab_webhook(request: Request, x_gitlab_token: str = Header(None)):
    # Validate GitLab token
    # Parse GitLab payload (different format from GitHub)
    # Publish to Kafka
```

**2. Add Cloudflare route:**
```yaml
ingress:
  - hostname: webhook.kitt.agency
    path: /gitlab
    service: http://192.168.68.10:8000
```

**3. Configure in GitLab:**
- Project → Settings → Webhooks
- URL: https://webhook.kitt.agency/gitlab
- Secret token: (different from GitHub)

---

### Future: Custom Webhooks (Non-Git)

**To support other services (Stripe, SendGrid, etc.):**

**1. Add endpoint** in Guardian:
```python
@app.post("/stripe")
async def stripe_webhook(request: Request):
    # Validate Stripe signature
    # Parse Stripe event
    # Publish to different Kafka topic (e.g., payment-events)
```

**2. Create new Kafka topic:**
```bash
ssh beast "docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic payment-events \
  --partitions 3 \
  --replication-factor 1"
```

**3. Create new worker** (or extend existing):
- Subscribe to `payment-events` topic
- Process payment events
- Execute custom actions

---

## 📝 Checklist: Adding a New Repository

**Before starting:**
- [ ] Repository exists on GitHub
- [ ] Repository cloned on Beast at `/home/jimmyb/repo-name`
- [ ] Docker compose configured (or none needed)
- [ ] You know the exact repository name as it appears in GitHub

**Step 1: Update Worker Config**
- [ ] Edit `beast/deployment-worker/deployment_worker.py`
- [ ] Add repository to `REPO_CONFIGS` dictionary
- [ ] Set correct paths (path, compose_path, compose_file)
- [ ] Set `enabled: True`
- [ ] Commit and push to GitHub

**Step 2: Deploy to Beast**
- [ ] Pull latest: `ssh beast "cd ~/dev-network && git pull origin main"`
- [ ] Restart worker: `ssh beast "pkill -f deployment_worker && cd ~/dev-network/beast/deployment-worker && nohup python3 deployment_worker.py > ~/deployment-worker-console.log 2>&1 &"`
- [ ] Verify running: `ssh beast "tail ~/deployment-worker.log | grep Connected"`

**Step 3: Add GitHub Webhook**
- [ ] Run `gh api repos/ORG/REPO/hooks --method POST ...` (see Step 3 above)
- [ ] Verify created: `gh api repos/ORG/REPO/hooks`
- [ ] Note webhook ID for future reference

**Step 4: Test**
- [ ] Trigger test: `gh api repos/ORG/REPO/hooks/ID/tests --method POST`
- [ ] OR: Push empty commit: `git commit --allow-empty -m "test" && git push`
- [ ] Check logs: `ssh beast "tail ~/deployment-worker.log"`
- [ ] Verify: Should see "✅ Deployment SUCCESSFUL"

**Step 5: Document**
- [ ] Add repository to `WEBHOOK-SYSTEM-OPERATIONS-GUIDE.md`
- [ ] Update `NEXT-SESSION-START-HERE.md` if needed
- [ ] Commit documentation

---

## 🔑 Important Information

### GitHub Webhook Secret

**Current Secret:**
```
0b263f5caf4c9d324c0a53c805a400681b0183a59d6a100ca64caf01d63e2e7d
```

**Location:**
- Guardian: `/home/jamesb/dev-network/guardian/webhook/.env`
- GitHub: Each repository's webhook settings

**To rotate secret:**
1. Generate new: `openssl rand -hex 32`
2. Update Guardian `.env` file
3. Update all GitHub webhooks with new secret
4. Restart Guardian webhook receiver

---

### Webhook URL

**Public endpoint:** `https://webhook.kitt.agency/github`

**This URL is the same for ALL repositories**
- Guardian receives webhook
- Identifies repository from payload
- Routes to correct deployment handler

---

### Repository Naming

**IMPORTANT:** Repository name in worker config must EXACTLY match what GitHub sends

**Check GitHub's repo name:**
```bash
gh api repos/ORG/REPO | jq '.name'
```

**Common issues:**
- Case sensitivity: `Mundus` vs `mundus`
- Hyphens vs underscores: `my-repo` vs `my_repo`

**Solution:** Add both variations to config if unsure

---

## 🎓 Advanced Usage

### Multiple Branches

**Current:** Only main/master branches trigger deployments

**To support feature branches:**

**1. Modify Guardian** to not filter branches:
```python
# Remove this check:
if branch not in ['main', 'master']:
    return {"status": "ignored"}
```

**2. Update worker** to handle branch in deployment:
```python
# Use branch parameter:
execute_command(f'git pull origin {branch}', cwd=repo_path)
```

---

### Different Deployment Actions

**Current:** All repos use `git pull + docker compose`

**To add custom deployment scripts:**

```python
def deploy_repo(repo_name: str, commit: str, branch: str):
    config = REPO_CONFIGS.get(repo_name)

    # Custom deployment script
    if repo_name == 'special-repo':
        execute_command('./deploy.sh', cwd=config['path'])
    else:
        # Standard git pull + docker compose
        ...
```

---

### Deployment Notifications

**To add Slack/Discord notifications on deployment:**

**1. Install webhook library:**
```bash
pip install discord-webhook
```

**2. Modify worker** to send notification:
```python
from discord_webhook import DiscordWebhook

def deploy_repo(...):
    result = execute_deployment()

    # Send Discord notification
    webhook = DiscordWebhook(url='your-discord-webhook-url')
    webhook.content = f"✅ Deployed {repo_name} (commit: {commit[:7]})"
    webhook.execute()
```

---

### Rollback on Failure

**To auto-rollback on failed deployment:**

```python
def deploy_repo(...):
    # Get current commit before pulling
    current_commit = execute_command('git rev-parse HEAD', cwd=repo_path)

    # Try deployment
    result = execute_deployment()

    if not result['success']:
        # Rollback
        logger.warning("Deployment failed, rolling back...")
        execute_command(f'git reset --hard {current_commit}', cwd=repo_path)
        execute_command('docker compose up -d --build', cwd=compose_path)
```

---

## 📊 Monitoring Your Webhooks

### View All Webhook Deliveries (GitHub)

```bash
# For a specific repo
gh api repos/ORG/REPO/hooks/WEBHOOK_ID/deliveries \
  | jq '.[] | {delivered_at, status: .status_code, event, guid}'

# Recent deliveries only
gh api repos/ORG/REPO/hooks/WEBHOOK_ID/deliveries \
  | jq '.[0:5] | .[] | {delivered_at, status: .status_code}'
```

### View Deployment Events (Kafka)

```bash
# All deployment webhooks
ssh beast "docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic deployment-webhooks \
  --from-beginning --timeout-ms 5000 2>/dev/null \
  | jq '{repo: .repo_name, commit: .commit[:7], timestamp}'"

# All deployment results
ssh beast "docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic deployment-results \
  --from-beginning --timeout-ms 5000 2>/dev/null \
  | jq '{repo: .repo_name, success, message, timestamp: .result_timestamp}'"
```

### Kafka UI Dashboard

**Access:** http://192.168.68.100:8082

**Navigate to:**
- Topics → deployment-webhooks (see incoming webhook events)
- Topics → deployment-results (see deployment outcomes)
- Consumers → deployment-worker (see processing lag)

---

## 🚀 Real-World Examples

### Example 1: Add dev-rag Auto-Deployment

**Scenario:** dev-rag now has docker-compose.yml, enable auto-deployment

**1. Update worker config:**
```python
'dev-rag': {
    'path': '/home/jimmyb/dev-rag',
    'compose_path': '/home/jimmyb/dev-rag',
    'compose_file': 'docker-compose.yml',
    'enabled': True  # Changed from False
}
```

**2. Commit and deploy:**
```bash
cd ~/dev-network
git add beast/deployment-worker/deployment_worker.py
git commit -m "feat: Enable auto-deployment for dev-rag"
git push origin main

ssh beast "cd ~/dev-network && git pull && pkill -f deployment_worker && \
  cd beast/deployment-worker && \
  nohup python3 deployment_worker.py > ~/deployment-worker-console.log 2>&1 &"
```

**3. Add GitHub webhook:**
```bash
gh api repos/Jimmyh-world/dev-rag/hooks \
  --method POST \
  --field name=web \
  --field active=true \
  --field events[]=push \
  --field config[url]=https://webhook.kitt.agency/github \
  --field config[content_type]=json \
  --field config[secret]=0b263f5caf4c9d324c0a53c805a400681b0183a59d6a100ca64caf01d63e2e7d
```

**4. Test:**
```bash
cd ~/dev-rag
git commit --allow-empty -m "test: Auto-deployment"
git push origin main

# Wait 5 seconds
ssh beast "tail ~/deployment-worker.log | grep dev-rag"
```

**Done!** dev-rag now auto-deploys on push.

---

### Example 2: Add New Microservice

**Scenario:** Created new microservice "api-gateway", want auto-deployment

**1. Clone repo on Beast:**
```bash
ssh beast "git clone git@github.com:YOUR-ORG/api-gateway.git ~/api-gateway"
```

**2. Create docker-compose.yml** (in repo or in dev-network):
```yaml
# ~/api-gateway/docker-compose.yml
version: '3.8'
services:
  api-gateway:
    build: .
    ports:
      - "9000:9000"
    restart: unless-stopped
```

**3. Add to worker config:**
```python
'api-gateway': {
    'path': '/home/jimmyb/api-gateway',
    'compose_path': '/home/jimmyb/api-gateway',
    'compose_file': 'docker-compose.yml',
    'enabled': True
}
```

**4. Commit, deploy, add webhook** (see steps above)

---

### Example 3: Add Multiple Repos at Once

**Scenario:** Adding 3 new repos (api-gateway, worker-service, scheduler)

**1. Update worker config** (add all 3):
```python
REPO_CONFIGS = {
    # ... existing ...
    'api-gateway': {...},
    'worker-service': {...},
    'scheduler': {...}
}
```

**2. Commit and deploy:**
```bash
git add beast/deployment-worker/deployment_worker.py
git commit -m "feat: Add auto-deployment for api-gateway, worker-service, scheduler"
git push origin main

ssh beast "cd ~/dev-network && git pull && pkill -f deployment_worker && \
  cd beast/deployment-worker && \
  nohup python3 deployment_worker.py > ~/deployment-worker-console.log 2>&1 &"
```

**3. Add webhooks** (run 3 times, once per repo):
```bash
for REPO in api-gateway worker-service scheduler; do
  gh api repos/YOUR-ORG/$REPO/hooks \
    --method POST \
    --field name=web \
    --field active=true \
    --field events[]=push \
    --field config[url]=https://webhook.kitt.agency/github \
    --field config[content_type]=json \
    --field config[secret]=0b263f5caf4c9d324c0a53c805a400681b0183a59d6a100ca64caf01d63e2e7d
done
```

**Done!** All 3 repos now auto-deploy.

---

## ⚠️ Common Gotchas

### Issue 1: Repository Name Mismatch

**Problem:** Worker can't find repo config

**Cause:** GitHub sends repo name that doesn't match config key

**Example:**
- GitHub sends: `Mundus-editor-application` (capital M)
- Config has: `mundus-editor-application` (lowercase m)

**Solution:** Add both variations to config:
```python
'mundus-editor-application': {...},
'Mundus-editor-application': {...},  # Add this too
```

---

### Issue 2: Repository Not Cloned on Beast

**Problem:** Git pull fails (repo doesn't exist)

**Cause:** Repository not cloned on Beast yet

**Solution:**
```bash
ssh beast "git clone git@github.com:ORG/REPO.git ~/repo-name"
```

---

### Issue 3: Docker Compose File Not Found

**Problem:** Docker compose fails (file not found)

**Cause:** Wrong `compose_path` in config

**Debug:**
```bash
# Find docker-compose.yml
ssh beast "find ~/repo-name -name 'docker-compose*.yml'"

# Update compose_path to match
```

---

### Issue 4: Worker Not Processing Events

**Problem:** Webhook received but no deployment

**Cause:** Worker stopped or crashed

**Debug:**
```bash
# Check worker running
ssh beast "ps aux | grep deployment_worker | grep -v grep"

# Check worker logs
ssh beast "tail -50 ~/deployment-worker.log"

# Restart worker
ssh beast "pkill -f deployment_worker && \
  cd ~/dev-network/beast/deployment-worker && \
  nohup python3 deployment_worker.py > ~/deployment-worker-console.log 2>&1 &"
```

---

### Issue 5: Cloudflare Tunnel Down

**Problem:** GitHub webhooks getting 502 errors

**Cause:** Cloudflare Tunnel not running on Beast

**Debug:**
```bash
# Check tunnel running
ssh beast "ps aux | grep cloudflared | grep -v grep"

# Restart tunnel
ssh beast "pkill cloudflared && \
  cd ~/dev-network/beast && \
  nohup cloudflared tunnel --config cloudflare/config.yml run > ~/cloudflared-tunnel.log 2>&1 &"

# Verify
curl https://webhook.kitt.agency/health
```

---

## 📁 File Locations

**Chromebook (Orchestrator):**
- Configuration: `/home/jimmyb/dev-network/`
- Worker config: `beast/deployment-worker/deployment_worker.py`
- Cloudflare config: `beast/cloudflare/config.yml`
- Documentation: `docs/`

**Guardian (Webhook Receiver):**
- Code: `/home/jamesb/dev-network/guardian/webhook/`
- Docker container: `webhook-receiver`
- Logs: `docker logs webhook-receiver`
- .env file: `/home/jamesb/dev-network/guardian/webhook/.env`

**Beast (Deployment Executor):**
- Worker code: `/home/jimmyb/dev-network/beast/deployment-worker/`
- Worker logs: `/home/jimmyb/deployment-worker.log`
- Kafka: `/home/jimmyb/dev-network/beast/kafka/`
- Cloudflare: `/home/jimmyb/dev-network/beast/cloudflare/`

---

## 🎓 System Architecture Summary

**Three-Machine Coordination:**
```
Chromebook (Orchestrator)
  ↓ Creates configs, commits to GitHub

GitHub (Source of Truth)
  ↓ Webhooks + Git pull

Guardian (Always-On Pi - Receiver)
  ↓ Receives webhooks, validates, queues

Kafka on Beast (Message Queue)
  ↓ Durable queue, audit trail

Beast (Powerful - Executor)
  ↓ Executes deployments, runs services
```

**Benefits:**
- ✅ Chromebook never executes (orchestrates only)
- ✅ Guardian always-on (low power Pi)
- ✅ Beast executes (powerful hardware)
- ✅ GitHub = source of truth (all configs committed)
- ✅ Kafka = audit trail (complete deployment history)

---

**Created:** 2025-10-21
**Status:** Production operational
**Use this guide when adding new repositories to auto-deployment system**

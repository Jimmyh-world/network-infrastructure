# Beast Infrastructure Cleanup Workflow

**Created:** 2025-10-17
**Purpose:** Clean up deployment inconsistencies after initial deployment
**Type:** Maintenance workflow following Jimmy's Workflow
**Status:** Ready for execution

---

## Issues to Fix

1. **3 duplicate cloudflared processes** running (should be 1)
2. **Unused cloudflared service** in docker-compose.yml (misleading config)
3. **Missing .env file** (Grafana using undefined variables)
4. **Tilde path** in docker-compose.yml needs to be absolute

---

## Pre-Execution Checklist

- [ ] All services currently running and functional
- [ ] Backup of current docker-compose.yml exists
- [ ] cloudflared tunnel currently connected (verify with `cloudflared tunnel info`)
- [ ] Working directory: `~/dev-network`

---

## Phase 1: Kill Duplicate cloudflared Processes

### 🔴 RED - Implementation

**Objective:** Stop all cloudflared processes, then start exactly ONE

**Step 1.1: Check current processes**
```bash
ps aux | grep "cloudflared tunnel" | grep -v grep
```

**Expected:** Should see 3 processes with same command

**Step 1.2: Kill all cloudflared processes**
```bash
pkill -f "cloudflared tunnel"
```

**Step 1.3: Verify all stopped**
```bash
ps aux | grep "cloudflared tunnel" | grep -v grep
```

**Expected:** No output (all processes stopped)

### 🟢 GREEN - Validation

**Step 1.4: Verify tunnel disconnected**
```bash
cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7
```

**Expected:** Should show "not connected" or error

**Success Criteria:**
- ✅ All cloudflared processes terminated
- ✅ Tunnel info shows disconnected state

### 🔵 CHECKPOINT

**Rollback if needed:**
```bash
# Restart tunnel (if needed to rollback)
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
```

**Gate:** ✅ All duplicate processes cleaned up

---

## Phase 2: Fix docker-compose.yml Configuration

### 🔴 RED - Implementation

**Objective:** Remove unused cloudflared service, fix tilde path, clean up volumes

**Step 2.1: Stop all Docker services**
```bash
cd ~/dev-network/beast/docker
docker compose down
```

**Step 2.2: Backup current config**
```bash
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)
```

**Step 2.3: Edit docker-compose.yml**

Remove these lines (138-157):
```yaml
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cloudflared
    restart: unless-stopped
    volumes:
      - ../cloudflare/config.yml:/etc/cloudflared/config.yml:ro
      - cloudflared-creds:/root/.cloudflared:ro
    networks:
      - monitoring
    command: tunnel run d2d710e7-94cd-41d8-9979-0519fa1233e7
    depends_on:
      - grafana
      - portainer
      - ydun-scraper
    healthcheck:
      test: ["CMD", "cloudflared", "tunnel", "info"]
      interval: 30s
      timeout: 5s
      retries: 3
```

Remove this volume definition (line 14-15):
```yaml
  cloudflared-creds:
    driver: local
```

Fix ydun-scraper context (line 123):
```yaml
# BEFORE
build:
  context: ~/ydun-scraper

# AFTER
build:
  context: /home/jimmyb/ydun-scraper
```

**Step 2.4: Validate YAML syntax**
```bash
docker compose config
```

**Expected:** Should parse successfully without errors

### 🟢 GREEN - Validation

**Step 2.5: Verify changes**
```bash
# Check cloudflared service removed
grep -c "cloudflared:" docker-compose.yml
```

**Expected:** 0 (service removed)

```bash
# Check tilde path fixed
grep "context:" docker-compose.yml
```

**Expected:** Should show `/home/jimmyb/ydun-scraper` (not `~`)

**Success Criteria:**
- ✅ YAML validates successfully
- ✅ cloudflared service removed
- ✅ Tilde path replaced with absolute path
- ✅ Backup created

### 🔵 CHECKPOINT

**Rollback if needed:**
```bash
cd ~/dev-network/beast/docker
cp docker-compose.yml.backup-YYYYMMDD-HHMMSS docker-compose.yml
```

**Gate:** ✅ docker-compose.yml cleaned and validated

---

## Phase 3: Verify/Create .env File

### 🔴 RED - Implementation

**Objective:** Ensure production .env exists with proper secrets

**Step 3.1: Check if .env already exists**
```bash
cd ~/dev-network/beast/docker
ls -la .env
```

**Expected:** Either file exists or "No such file or directory"

**Step 3.2: Create .env if missing**
```bash
# Only if .env doesn't exist
if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env created from template"
else
  echo ".env already exists"
fi
```

**Step 3.3: Verify .env contents**
```bash
cat .env
```

**Check:** Does it have secure values or template defaults?

**Step 3.4: Edit .env with production values (if needed)**

Generate secure password:
```bash
openssl rand -base64 32
```

Edit .env:
```bash
nano .env
```

Update these values:
```env
# Grafana Configuration
GF_SECURITY_ADMIN_PASSWORD=<GENERATED_PASSWORD_HERE>
GF_SERVER_ROOT_URL=https://grafana.kitt.agency
GF_INSTALL_PLUGINS=

# Optional: Prometheus retention (already set in docker-compose)
PROMETHEUS_RETENTION=720h
```

**Step 3.5: Secure .env permissions**
```bash
chmod 600 .env
ls -la .env
```

**Expected:** `-rw-------` (only owner can read/write)

### 🟢 GREEN - Validation

**Step 3.6: Verify .env values**
```bash
cat .env | grep "GF_SECURITY_ADMIN_PASSWORD"
```

**Expected:** Should show a secure password (not "admin123")

```bash
cat .env | grep "GF_SERVER_ROOT_URL"
```

**Expected:** `https://grafana.kitt.agency`

**Success Criteria:**
- ✅ .env file exists (either already there or newly created)
- ✅ Secure password set (not "admin123")
- ✅ Correct domain configured (grafana.kitt.agency)
- ✅ File permissions secured (600)

### 🔵 CHECKPOINT

**Rollback if needed:**
```bash
# Delete .env if issues
rm .env
```

**Gate:** ✅ .env file created with production secrets

---

## Phase 4: Restart Docker Services

### 🔴 RED - Implementation

**Objective:** Restart all Docker services with clean config

**Step 4.1: Start services**
```bash
cd ~/dev-network/beast/docker
docker compose up -d
```

**Step 4.2: Wait for services to start**
```bash
sleep 10
```

**Step 4.3: Check service status**
```bash
docker compose ps
```

**Expected:** All 6 services "Up" and healthy

### 🟢 GREEN - Validation

**Step 4.4: Verify each service health**
```bash
# Prometheus
curl -s http://localhost:9090/-/healthy

# Node Exporter
curl -s http://localhost:9100/metrics | head -5

# cAdvisor
curl -s http://localhost:8080/healthz

# Grafana
curl -s http://localhost:3000/api/health

# Portainer
curl -k -s https://localhost:9443 | head -5

# Ydun Scraper
curl -s http://localhost:5000/health
```

**Expected:** All return successful responses

**Step 4.5: Check Docker logs**
```bash
docker compose logs --tail 20
```

**Expected:** No error messages

**Success Criteria:**
- ✅ All 6 Docker services running
- ✅ All health checks passing
- ✅ No error messages in logs
- ✅ Grafana using new admin password

### 🔵 CHECKPOINT

**Rollback if needed:**
```bash
cd ~/dev-network/beast/docker
docker compose down
docker compose -f docker-compose.yml.backup-YYYYMMDD-HHMMSS up -d
```

**Gate:** ✅ All Docker services running cleanly

---

## Phase 5: Start Single cloudflared Process

### 🔴 RED - Implementation

**Objective:** Start exactly ONE cloudflared tunnel process on host

**Step 5.1: Clear old log**
```bash
rm -f /tmp/cloudflared.log
```

**Step 5.2: Start tunnel**
```bash
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
```

**Step 5.3: Wait for startup**
```bash
sleep 5
```

**Step 5.4: Check process count**
```bash
ps aux | grep "cloudflared tunnel" | grep -v grep | wc -l
```

**Expected:** Exactly 1

### 🟢 GREEN - Validation

**Step 5.5: Check tunnel status**
```bash
cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7
```

**Expected:** Should show "Connected" with 4 edge connections

**Step 5.6: Check logs**
```bash
tail -50 /tmp/cloudflared.log
```

**Expected:** Should show "Connection ... registered"

**Step 5.7: Test external access**
```bash
# Grafana
curl -s -o /dev/null -w "%{http_code}" https://grafana.kitt.agency/api/health

# Scraper
curl -s -o /dev/null -w "%{http_code}" https://scrape.kitt.agency/health
```

**Expected:** Both return `200`

**Success Criteria:**
- ✅ Exactly 1 cloudflared process running
- ✅ Tunnel connected to Cloudflare edge
- ✅ External HTTPS access working
- ✅ Logs show no errors

### 🔵 CHECKPOINT

**Rollback if needed:**
```bash
pkill -f "cloudflared tunnel"
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
```

**Gate:** ✅ Single tunnel process running and connected

---

## Phase 6: Final Validation

### 🔴 RED - Implementation

**Objective:** End-to-end validation of entire stack

**Step 6.1: Verify Docker services**
```bash
docker compose ps
docker stats --no-stream
```

**Step 6.2: Verify tunnel**
```bash
ps aux | grep "cloudflared tunnel" | grep -v grep | wc -l
cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7
```

### 🟢 GREEN - Validation

**Step 6.3: Test internal endpoints**
```bash
# All should return 200 or valid response
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:9090/-/healthy
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:9100/metrics
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/healthz
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/api/health
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/health
```

**Step 6.4: Test external HTTPS endpoints**
```bash
# Grafana
curl -s https://grafana.kitt.agency/api/health | jq .

# Scraper
curl -s https://scrape.kitt.agency/health | jq .
```

**Step 6.5: Test scraper functionality**
```bash
curl -X POST https://scrape.kitt.agency/scrape \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.bbc.com/news/world"]}' | jq '.stats'
```

**Expected:** Should extract article successfully

**Success Criteria:**
- ✅ 6 Docker services healthy
- ✅ 1 cloudflared process running
- ✅ All internal endpoints responding
- ✅ All external HTTPS endpoints working
- ✅ Scraper extracting articles successfully
- ✅ Grafana accessible with new password

### 🔵 CHECKPOINT

**Final Status Report:**
```bash
echo "=== Docker Services ==="
docker compose ps

echo -e "\n=== Cloudflared Process ==="
ps aux | grep "cloudflared tunnel" | grep -v grep | wc -l

echo -e "\n=== Tunnel Status ==="
cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7

echo -e "\n=== Resource Usage ==="
docker stats --no-stream
```

**Gate:** ✅ Complete infrastructure running cleanly

---

## Phase 7: Commit and Document

### 🔴 RED - Implementation

**Objective:** Commit cleaned configuration and document changes

**Step 7.1: Check git status**
```bash
cd ~/dev-network
git status
```

**Step 7.2: Add changes**
```bash
git add beast/docker/docker-compose.yml
git add beast/docs/INFRASTRUCTURE-CLEANUP-WORKFLOW.md
```

**Step 7.3: Commit with descriptive message**
```bash
git commit -m "$(cat <<'EOF'
refactor: Clean up Beast infrastructure configuration

Changes:
- Remove unused cloudflared Docker service (runs on host instead)
- Fix tilde path to absolute path in ydun-scraper context
- Remove cloudflared-creds volume (unused)
- Create .env file with production secrets
- Kill duplicate cloudflared processes (3 → 1)
- Validate complete stack functionality

All services tested and operational.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Step 7.4: Push to GitHub**
```bash
git push origin main
```

### 🟢 GREEN - Validation

**Step 7.5: Verify commit**
```bash
git log -1 --stat
```

**Expected:** Should show commit with file changes

**Step 7.6: Verify push**
```bash
git status
```

**Expected:** "Your branch is up to date with 'origin/main'"

**Success Criteria:**
- ✅ Changes committed to git
- ✅ Pushed to GitHub
- ✅ Clean working directory

### 🔵 CHECKPOINT

**Gate:** ✅ Configuration cleanup documented in git history

---

## Phase 8: Update Documentation

### 🔴 RED - Implementation

**Objective:** Create documentation explaining host-based tunnel deployment

**Step 8.1: Create tunnel deployment guide**

Create `beast/cloudflare/TUNNEL-HOST-DEPLOYMENT.md`:

```markdown
# Cloudflare Tunnel - Host-Based Deployment

**Created:** 2025-10-17
**Type:** Host process (not Docker container)
**Rationale:** Direct localhost access without Docker network abstraction

---

## Why Host-Based?

The cloudflared tunnel runs directly on the Beast host (not in a Docker container) for these reasons:

1. **Credential Access:** Easier access to ~/.cloudflared credentials
2. **Localhost Routing:** Direct access to localhost:PORT without Docker bridge network
3. **User Permissions:** No container user permission issues
4. **Simplicity:** One less container to manage

---

## Current Configuration

**Tunnel ID:** d2d710e7-94cd-41d8-9979-0519fa1233e7
**Config File:** ~/dev-network/beast/cloudflare/config.yml
**Credentials:** ~/.cloudflared/d2d710e7-94cd-41d8-9979-0519fa1233e7.json
**Log File:** /tmp/cloudflared.log

---

## Managing the Tunnel

### Start Tunnel
\`\`\`bash
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
\`\`\`

### Stop Tunnel
\`\`\`bash
pkill -f "cloudflared tunnel"
\`\`\`

### Check Status
\`\`\`bash
# Process check
ps aux | grep "cloudflared tunnel" | grep -v grep

# Tunnel info
cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7

# View logs
tail -50 /tmp/cloudflared.log
\`\`\`

---

## Troubleshooting

### Multiple Processes Running

If you see multiple cloudflared processes:
\`\`\`bash
# Kill all
pkill -f "cloudflared tunnel"

# Start one
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
\`\`\`

### Tunnel Not Connecting

Check credentials:
\`\`\`bash
ls -la ~/.cloudflared/
\`\`\`

Should see:
- cert.pem (account auth)
- d2d710e7-94cd-41d8-9979-0519fa1233e7.json (tunnel credentials)

### 502 Errors

Check services are running:
\`\`\`bash
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:5000/health      # Scraper
\`\`\`

---

**Last Updated:** 2025-10-17
```

**Step 8.2: Update README.md**

Add section about cloudflared:
```markdown
## Cloudflare Tunnel (Host-Based)

**Important:** The cloudflared tunnel runs on the host, NOT in Docker.

See: `beast/cloudflare/TUNNEL-HOST-DEPLOYMENT.md`

Manage tunnel:
- Start: `cd ~/dev-network/beast && nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &`
- Stop: `pkill -f "cloudflared tunnel"`
- Status: `cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7`
```

### 🟢 GREEN - Validation

**Step 8.3: Verify documentation**
```bash
ls -la beast/cloudflare/TUNNEL-HOST-DEPLOYMENT.md
cat beast/cloudflare/TUNNEL-HOST-DEPLOYMENT.md | head -20
```

**Success Criteria:**
- ✅ TUNNEL-HOST-DEPLOYMENT.md created
- ✅ README.md updated
- ✅ Clear explanation of host-based approach

### 🔵 CHECKPOINT

**Gate:** ✅ Architecture documented

---

## Phase 9: Final Commit

### 🔴 RED - Implementation

**Step 9.1: Add documentation**
```bash
git add beast/cloudflare/TUNNEL-HOST-DEPLOYMENT.md
git add README.md
```

**Step 9.2: Commit**
```bash
git commit -m "$(cat <<'EOF'
docs: Add cloudflared host-based deployment documentation

- Explain why tunnel runs on host (not Docker)
- Document tunnel management commands
- Add troubleshooting procedures
- Update README with tunnel architecture

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Step 9.3: Push**
```bash
git push origin main
```

### 🟢 GREEN - Validation

**Step 9.4: Verify**
```bash
git log -2 --oneline
```

**Expected:** Should show 2 new commits (cleanup + docs)

**Success Criteria:**
- ✅ Documentation committed
- ✅ Pushed to GitHub

### 🔵 CHECKPOINT

**Gate:** ✅ Complete cleanup workflow executed and documented

---

## Cleanup Complete - Final Status

**Infrastructure:**
- ✅ 6 Docker services running (Prometheus, Node Exporter, cAdvisor, Grafana, Portainer, ydun-scraper)
- ✅ 1 cloudflared process on host (not Docker)
- ✅ Clean docker-compose.yml (no unused services)
- ✅ Production .env with secure secrets
- ✅ Absolute paths (no tildes)

**External Access:**
- ✅ https://grafana.kitt.agency (working)
- ✅ https://scrape.kitt.agency (working)
- ✅ https://portainer.kitt.agency (self-signed cert issue remains)

**Git:**
- ✅ 2 commits pushed (cleanup + documentation)
- ✅ Clean working directory

**Documentation:**
- ✅ INFRASTRUCTURE-CLEANUP-WORKFLOW.md (this file)
- ✅ TUNNEL-HOST-DEPLOYMENT.md (tunnel management)
- ✅ README.md updated

---

**Next Steps:**
1. Integrate ydun-scraper with Mundus Supabase edge function
2. Set up Grafana admin access with new password
3. Monitor baseline performance metrics

---

**Last Updated:** 2025-10-17

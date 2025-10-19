# Ydun Scraper Deployment - Beast Infrastructure

**Created**: 2025-10-17
**Machine**: Beast (thebeast - 192.168.68.100)
**Workflow**: RED/GREEN/CHECKPOINT (Jimmy's Workflow v1.1)
**Status**: Ready for Execution
**Domain**: kitt.agency
**Scraper URL**: https://scrape.kitt.agency

---

## Overview

This document defines the complete RED/GREEN/CHECKPOINT workflow for deploying the ydun-scraper microservice alongside the existing Beast monitoring infrastructure.

### Infrastructure Components

**Existing (from previous workflow):**
- Prometheus (metrics collection)
- Grafana (dashboards)
- Node Exporter (system metrics)
- cAdvisor (container metrics)
- Portainer (Docker management)
- Cloudflare Tunnel (HTTPS access)

**Adding:**
- **ydun-scraper** - Article scraping microservice for Mundus

### Success Criteria

- ✅ ydun-scraper repo cloned to Beast
- ✅ ydun-scraper service added to docker-compose.yml
- ✅ All Cloudflare routes updated to kitt.agency
- ✅ scrape.kitt.agency route configured
- ✅ Complete stack deployed (7 services running)
- ✅ External HTTPS access validated for all services
- ✅ Mundus can call scrape.kitt.agency successfully

---

## Pre-Execution Checklist

Before starting, verify:

- [x] Monitoring infrastructure workflow complete (MONITORING-INFRASTRUCTURE-SETUP.md)
- [x] Docker installed and operational: `docker --version`
- [x] Git configured: `git config --list`
- [x] Domain active on Cloudflare: kitt.agency
- [x] ydun-scraper repo exists: https://github.com/Jimmyh-world/ydun-scraper
- [ ] Sufficient disk space: `df -h` (expect: >20GB free)

---

## Phase 1: Clone ydun-scraper Repository

### Step 1.1: Clone Scraper to Beast

🔴 **IMPLEMENT:**
- Clone ydun-scraper repo to Beast home directory
- Verify source code and Dockerfile present
- Check dependencies in requirements.txt
- Complexity: 🟢 Simple
- Estimated: 5 minutes
- Commands:
```bash
cd ~
git clone https://github.com/Jimmyh-world/ydun-scraper.git
cd ydun-scraper
ls -la
```

🟢 **VALIDATE:**
- Run: `test -d ~/ydun-scraper && echo "✅ Repo cloned"` (expect: repo exists)
- Run: `test -f ~/ydun-scraper/Dockerfile && echo "✅ Dockerfile present"` (expect: Dockerfile found)
- Run: `test -f ~/ydun-scraper/src/http_server.py && echo "✅ HTTP server present"` (expect: server code found)
- Run: `cat ~/ydun-scraper/requirements.txt` (expect: trafilatura, Flask, etc.)
- Verify: AGENTS.md, CLAUDE.md, JIMMYS-WORKFLOW.md present (template compliance)

🔵 **CHECKPOINT:** ydun-scraper Repository Cloned
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 5 minutes
**Actual**: [TBD]
**Tests**: ✅ Repository cloned, ✅ Source files present
**Rollback**: `rm -rf ~/ydun-scraper`
**Dependencies**: None (external GitHub repo)
**Blockers**: None
**Notes**: Independent microservice repo, not part of dev-network

---

## Phase 2: Update Cloudflare Configuration for kitt.agency

### Step 2.1: Replace Domain in Cloudflare Config

🔴 **IMPLEMENT:**
- Edit beast/cloudflare/config.yml
- Replace all instances of "yourdomain.com" with "kitt.agency"
- Add route for scraper: scrape.kitt.agency → http://ydun-scraper:8080
- Complexity: 🟢 Simple
- Estimated: 5 minutes
- Files to modify:
  - beast/cloudflare/config.yml

🟢 **VALIDATE:**
- Run: `grep "kitt.agency" beast/cloudflare/config.yml` (expect: 3 hostnames found)
- Run: `grep "yourdomain.com" beast/cloudflare/config.yml` (expect: NO matches)
- Check: grafana.kitt.agency route exists
- Check: portainer.kitt.agency route exists
- Check: scrape.kitt.agency route exists
- Verify: scrape.kitt.agency → http://ydun-scraper:8080
- Run: `cat beast/cloudflare/config.yml` (manual review for correctness)

🔵 **CHECKPOINT:** Cloudflare Config Updated for kitt.agency
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 5 minutes
**Actual**: [TBD]
**Tests**: ✅ Domain updated, ✅ Scraper route added
**Rollback**: `git checkout beast/cloudflare/config.yml`
**Dependencies**: None
**Blockers**: None
**Notes**: Cloudflare tunnel will use this config when started

---

## Phase 3: Add ydun-scraper to Docker Compose

### Step 3.1: Add Scraper Service Definition

🔴 **IMPLEMENT:**
- Add ydun-scraper service to beast/docker/docker-compose.yml
- Configuration:
  - Build context: ~/ydun-scraper (not image:, use build:)
  - Container name: ydun-scraper
  - Port: 8080:8080
  - Command: python src/http_server.py (HTTP mode)
  - Health check: curl -f http://localhost:8080/health
  - Network: monitoring
  - Restart policy: unless-stopped
- Complexity: 🟡 Moderate
- Estimated: 10 minutes
- Files to modify:
  - beast/docker/docker-compose.yml

🟢 **VALIDATE:**
- Run: `cd ~/dev-network/beast/docker && docker compose config` (expect: valid YAML)
- Check: ydun-scraper service defined
- Check: Build context points to ~/ydun-scraper
- Check: Port 8080:8080 exposed
- Check: Health check configured
- Check: Connected to monitoring network
- Verify: No syntax errors in YAML

🔵 **CHECKPOINT:** ydun-scraper Added to Docker Compose
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 10 minutes
**Actual**: [TBD]
**Tests**: ✅ YAML valid, ✅ Service configured
**Rollback**: `git checkout beast/docker/docker-compose.yml`
**Dependencies**: Step 1.1 (COMPLETE - repo cloned)
**Blockers**: None
**Notes**: Build step will occur during docker compose up

---

## Phase 4: Create Environment Configuration

### Step 4.1: Create .env File from Template

🔴 **IMPLEMENT:**
- Copy beast/docker/.env.example to beast/docker/.env
- Set GF_SECURITY_ADMIN_PASSWORD (generate strong password)
- Set GF_SERVER_ROOT_URL=https://grafana.kitt.agency
- Set GF_INSTALL_PLUGINS (empty or specify plugins)
- Complexity: 🟢 Simple
- Estimated: 5 minutes
- Files to create:
  - beast/docker/.env (NOT committed to git - secrets)

🟢 **VALIDATE:**
- Run: `test -f ~/dev-network/beast/docker/.env && echo "✅ .env created"` (expect: file exists)
- Run: `grep "kitt.agency" ~/dev-network/beast/docker/.env` (expect: kitt.agency found)
- Run: `grep "GF_SECURITY_ADMIN_PASSWORD" ~/dev-network/beast/docker/.env` (expect: password set, not "admin123")
- Run: `git status | grep ".env"` (expect: NOT listed - file is gitignored)
- Check: .env file is gitignored (already verified in .gitignore)
- Verify: No placeholder values remain

🔵 **CHECKPOINT:** Environment File Created
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 5 minutes
**Actual**: [TBD]
**Tests**: ✅ File created, ✅ Passwords set, ✅ Not in git
**Rollback**: `rm ~/dev-network/beast/docker/.env`
**Dependencies**: None
**Blockers**: None
**Notes**: Contains secrets - never commit to git

---

## Phase 5: Deploy Complete Stack

### Step 5.1: Build and Start All Services

🔴 **IMPLEMENT:**
- Navigate to docker directory
- Build ydun-scraper image (first time build)
- Start all 7 services via docker compose
- Monitor startup logs for errors
- Complexity: 🟡 Moderate
- Estimated: 10 minutes (includes image build time)
- Commands:
```bash
cd ~/dev-network/beast/docker

# Build ydun-scraper image
docker compose build ydun-scraper

# Start all services
docker compose up -d

# Wait for containers to initialize
sleep 30

# Check all running
docker compose ps
```

🟢 **VALIDATE:**
- Run: `docker compose ps` (expect: 7 containers running)
  - prometheus
  - node-exporter
  - cadvisor
  - grafana
  - portainer
  - cloudflared
  - ydun-scraper
- Run: `docker ps --format "table {{.Names}}\t{{.Status}}"` (expect: all "Up" status)
- Run: `curl -s http://localhost:8080/health` (expect: {"status":"healthy"} or similar)
- Run: `curl -s http://localhost:9090/-/healthy` (expect: Prometheus is Healthy)
- Run: `curl -s http://localhost:3000/api/health` (expect: {"database":"ok"})
- Run: `curl -k -I https://localhost:9443` (expect: HTTP 200)
- Check: `docker compose logs | grep -i error` (expect: no critical errors)
- Check: `docker stats --no-stream` (expect: reasonable resource usage)

🔵 **CHECKPOINT:** Complete Stack Deployed
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 10 minutes
**Actual**: [TBD]
**Tests**: ✅ All 7 containers running, ✅ Health checks passing
**Rollback**:
```bash
cd ~/dev-network/beast/docker
docker compose down
docker volume rm beast_prometheus-data beast_grafana-data beast_portainer-data
```
**Dependencies**: Steps 2.1, 3.1, 4.1 (COMPLETE)
**Blockers**: None
**Notes**: First build of ydun-scraper may take 2-5 minutes

---

## Phase 6: Configure Cloudflare Tunnel

### Step 6.1: Install Cloudflare Tunnel CLI

🔴 **IMPLEMENT:**
- Download cloudflared for Linux
- Install via dpkg
- Verify installation
- Complexity: 🟢 Simple
- Estimated: 5 minutes
- Commands:
```bash
cd /tmp
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
cloudflared --version
```

🟢 **VALIDATE:**
- Run: `cloudflared --version` (expect: version number displayed)
- Run: `which cloudflared` (expect: /usr/local/bin/cloudflared or similar)

🔵 **CHECKPOINT:** Cloudflared CLI Installed
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 5 minutes
**Actual**: [TBD]
**Tests**: ✅ CLI installed and accessible
**Rollback**: `sudo apt remove cloudflared`
**Dependencies**: None
**Blockers**: None

---

### Step 6.2: Authenticate and Create Tunnel

🔴 **IMPLEMENT:**
- Authenticate with Cloudflare account (browser opens)
- Create tunnel named "beast-tunnel"
- Verify tunnel credentials stored
- Complexity: 🟡 Moderate (requires user interaction)
- Estimated: 10 minutes (includes user authentication)
- Commands:
```bash
# Login to Cloudflare (opens browser)
cloudflared tunnel login
# USER ACTION REQUIRED: Login to Cloudflare, select kitt.agency domain, authorize

# Create tunnel
cloudflared tunnel create beast-tunnel

# List tunnels to verify
cloudflared tunnel list
```

🟢 **VALIDATE:**
- Run: `cloudflared tunnel list` (expect: beast-tunnel listed)
- Run: `ls -la ~/.cloudflared/` (expect: *.json credentials file)
- Check: Credentials file is valid JSON: `cat ~/.cloudflared/*.json | jq` (expect: valid JSON)
- Verify: Tunnel UUID matches credentials file

🔵 **CHECKPOINT:** Cloudflare Tunnel Created
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 10 minutes
**Actual**: [TBD]
**Tests**: ✅ Tunnel created, ✅ Credentials stored
**Rollback**: `cloudflared tunnel delete beast-tunnel && rm ~/.cloudflared/*.json`
**Dependencies**: Step 6.1 (COMPLETE)
**Blockers**: Requires user authentication in browser
**Notes**: Browser will open for Cloudflare authentication

---

### Step 6.3: Create DNS Routes

🔴 **IMPLEMENT:**
- Create CNAME DNS records for all subdomains
- Point to Cloudflare Tunnel
- Verify records created in Cloudflare
- Complexity: 🟢 Simple
- Estimated: 5 minutes
- Commands:
```bash
# Create DNS routes for all services
cloudflared tunnel route dns beast-tunnel grafana.kitt.agency
cloudflared tunnel route dns beast-tunnel portainer.kitt.agency
cloudflared tunnel route dns beast-tunnel scrape.kitt.agency

# Verify routes
cloudflared tunnel route list
```

🟢 **VALIDATE:**
- Run: `cloudflared tunnel route list` (expect: 3 routes listed)
- Run: `nslookup grafana.kitt.agency` (expect: CNAME to tunnel)
- Run: `nslookup portainer.kitt.agency` (expect: CNAME to tunnel)
- Run: `nslookup scrape.kitt.agency` (expect: CNAME to tunnel)
- Check: All 3 routes point to beast-tunnel

🔵 **CHECKPOINT:** DNS Routes Configured
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 5 minutes
**Actual**: [TBD]
**Tests**: ✅ 3 DNS routes created
**Rollback**:
```bash
cloudflared tunnel route delete grafana.kitt.agency
cloudflared tunnel route delete portainer.kitt.agency
cloudflared tunnel route delete scrape.kitt.agency
```
**Dependencies**: Step 6.2 (COMPLETE)
**Blockers**: None
**Notes**: DNS propagation may take a few minutes

---

### Step 6.4: Update Cloudflare Config and Restart Tunnel

🔴 **IMPLEMENT:**
- Verify beast/cloudflare/config.yml has correct tunnel ID
- Update tunnel reference in config.yml if needed
- Restart cloudflared container to pick up DNS routes
- Complexity: 🟢 Simple
- Estimated: 5 minutes
- Commands:
```bash
# Get tunnel UUID
cloudflared tunnel list | grep beast-tunnel

# Verify config.yml has correct tunnel ID
cat ~/dev-network/beast/cloudflare/config.yml | grep "tunnel:"

# Restart cloudflared container
cd ~/dev-network/beast/docker
docker compose restart cloudflared

# Check tunnel logs
docker logs cloudflared --tail 20
```

🟢 **VALIDATE:**
- Run: `docker ps | grep cloudflared` (expect: container running)
- Run: `docker logs cloudflared | grep -i "connection"` (expect: "registered tunnel connection" or similar)
- Check: Cloudflare Dashboard → Access → Tunnels → beast-tunnel (expect: HEALTHY status)
- Run: `docker logs cloudflared | grep -i error` (expect: no critical errors)

🔵 **CHECKPOINT:** Cloudflare Tunnel Running
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 5 minutes
**Actual**: [TBD]
**Tests**: ✅ Tunnel connected and healthy
**Rollback**: `docker compose stop cloudflared`
**Dependencies**: Step 6.3 (COMPLETE)
**Blockers**: None
**Notes**: Tunnel must show HEALTHY in Cloudflare dashboard

---

## Phase 7: End-to-End Validation

### Step 7.1: Validate All Internal Services

🔴 **IMPLEMENT:**
- No changes - validation only
- Test all services accessible locally
- Verify metrics collection working
- Check container health
- Complexity: 🟢 Simple
- Estimated: 10 minutes

🟢 **VALIDATE:**

**Docker Health:**
```bash
# All 7 containers running
docker compose ps
# Expected: 7 services, all UP

# Container resource usage
docker stats --no-stream
# Expected: All containers healthy, total <2GB RAM
```

**Service Health Checks:**
```bash
# Prometheus
curl -s http://localhost:9090/-/healthy
# Expected: Prometheus is Healthy

# Grafana
curl -s http://localhost:3000/api/health | jq '.database'
# Expected: "ok"

# Portainer
curl -k -I https://localhost:9443
# Expected: HTTP 200

# Ydun Scraper
curl -s http://localhost:8080/health
# Expected: {"status": "healthy"} or similar

# Node Exporter
curl -s http://localhost:9100/metrics | head -5
# Expected: Metrics output

# cAdvisor
curl -s http://localhost:8080/healthz
# Expected: ok
```

**Metrics Collection:**
```bash
# Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'
# Expected: 3 targets (prometheus, node-exporter, cadvisor)

# All targets UP
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
# Expected: All show health: "up"
```

🔵 **CHECKPOINT:** Internal Services Validated
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 10 minutes
**Actual**: [TBD]
**Tests**: ✅ All services healthy
**Rollback**: N/A (validation only)
**Dependencies**: Step 5.1 (COMPLETE - stack deployed)
**Blockers**: None

---

### Step 7.2: Validate External HTTPS Access

🔴 **IMPLEMENT:**
- No changes - validation only
- Test external HTTPS access to all 3 services
- Verify SSL certificates valid
- Test from external network (mobile hotspot recommended)
- Complexity: 🟡 Moderate (requires external network)
- Estimated: 15 minutes

🟢 **VALIDATE:**

**From Local Network (192.168.68.x):**
```bash
# Grafana
curl -I https://grafana.kitt.agency
# Expected: HTTP 200 (or 302 redirect to login)

# Portainer
curl -k -I https://portainer.kitt.agency
# Expected: HTTP 200

# Ydun Scraper
curl -I https://scrape.kitt.agency/health
# Expected: HTTP 200
```

**From External Network (mobile hotspot or different network):**
```bash
# Grafana accessible
curl -I https://grafana.kitt.agency
# Expected: HTTP 200, no certificate warnings

# Portainer accessible
curl -I https://portainer.kitt.agency
# Expected: HTTP 200

# Ydun Scraper health check
curl https://scrape.kitt.agency/health
# Expected: {"status": "healthy"}

# Verify Cloudflare is proxying (check headers)
curl -I https://scrape.kitt.agency | grep -i cloudflare
# Expected: Cloudflare headers present (CF-RAY, etc.)
```

**Browser Tests:**
- Navigate to: https://grafana.kitt.agency
  - ✅ Login page loads
  - ✅ No SSL warnings
  - ✅ Can login with credentials from .env
  - ✅ Dashboards visible

- Navigate to: https://portainer.kitt.agency
  - ✅ Login/setup page loads
  - ✅ No SSL warnings
  - ✅ Can create admin account (first time) or login
  - ✅ All 7 containers visible

🔵 **CHECKPOINT:** External HTTPS Access Validated
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 15 minutes
**Actual**: [TBD]
**Tests**: ✅ All services accessible via HTTPS, ✅ SSL valid, ✅ Cloudflare proxy working
**Rollback**: N/A (validation only)
**Dependencies**: Step 6.4 (COMPLETE - tunnel running)
**Blockers**: Requires external network for testing
**Notes**: DNS propagation may take 1-5 minutes

---

### Step 7.3: Test Ydun Scraper Functionality

🔴 **IMPLEMENT:**
- No changes - validation only
- Test scraper endpoint with real URL
- Verify article extraction works
- Test from local and external
- Complexity: 🟡 Moderate
- Estimated: 10 minutes

🟢 **VALIDATE:**

**Local Test:**
```bash
# Test scraper endpoint
curl -X POST http://localhost:8080/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.bbc.com/news"}' | jq

# Expected: JSON response with article data (title, content, etc.)
```

**External Test (via Cloudflare Tunnel):**
```bash
# From external network (or use Postman/browser)
curl -X POST https://scrape.kitt.agency/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.bbc.com/news"}' | jq

# Expected: Same JSON response as local test
```

**Validation Criteria:**
- ✅ Scraper returns valid JSON
- ✅ Article title extracted
- ✅ Article content extracted
- ✅ No errors in response
- ✅ External HTTPS access works
- ✅ Response time reasonable (<5 seconds)

🔵 **CHECKPOINT:** Ydun Scraper Functional
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 10 minutes
**Actual**: [TBD]
**Tests**: ✅ Scraper works locally, ✅ External HTTPS access works
**Rollback**: N/A (validation only)
**Dependencies**: Steps 5.1, 6.4 (COMPLETE)
**Blockers**: None
**Notes**: Ready for Mundus integration

---

## Phase 8: Documentation and Handoff

### Step 8.1: Update Network Infrastructure README

🔴 **IMPLEMENT:**
- Update main README.md with ydun-scraper information
- Add scrape.kitt.agency to service URLs
- Document scraper purpose and usage
- Complexity: 🟢 Simple
- Estimated: 5 minutes
- Files to modify:
  - README.md

🟢 **VALIDATE:**
- Check: README.md contains ydun-scraper section
- Check: scrape.kitt.agency URL documented
- Verify: Clear description of scraper purpose
- Verify: Usage examples included

🔵 **CHECKPOINT:** Documentation Updated
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 5 minutes
**Actual**: [TBD]
**Tests**: ✅ Documentation complete
**Rollback**: `git checkout README.md`
**Dependencies**: All previous steps (COMPLETE)
**Blockers**: None

---

### Step 8.2: Create Mundus Integration Guide

🔴 **IMPLEMENT:**
- Create beast/docs/MUNDUS-INTEGRATION.md
- Document how Mundus Supabase edge function should call scraper
- Include example edge function code
- Document expected request/response format
- Complexity: 🟢 Simple
- Estimated: 10 minutes
- Files to create:
  - beast/docs/MUNDUS-INTEGRATION.md

🟢 **VALIDATE:**
- Check: Integration guide created
- Check: Includes scrape.kitt.agency URL
- Check: Example request/response documented
- Check: Edge function code snippet included

🔵 **CHECKPOINT:** Mundus Integration Guide Complete
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 10 minutes
**Actual**: [TBD]
**Tests**: ✅ Guide created and complete
**Rollback**: `rm beast/docs/MUNDUS-INTEGRATION.md`
**Dependencies**: None
**Blockers**: None

---

## Complete Workflow Summary

**Total Phases:** 8
**Total Steps:** 10
**Estimated Time:** 90 minutes (includes Cloudflare authentication wait)
**Complexity:** Mostly Simple, Some Moderate

**Phase Breakdown:**
- Phase 1: Clone scraper repo (5 min)
- Phase 2: Update Cloudflare config (5 min)
- Phase 3: Add to docker-compose (10 min)
- Phase 4: Create .env (5 min)
- Phase 5: Deploy stack (10 min)
- Phase 6: Cloudflare Tunnel (25 min - includes auth)
- Phase 7: Validation (35 min)
- Phase 8: Documentation (15 min)

---

## Rollback Strategy

**Full Rollback:**
```bash
# Stop all services
cd ~/dev-network/beast/docker
docker compose down -v

# Delete tunnel
cloudflared tunnel delete beast-tunnel
rm -rf ~/.cloudflared/

# Remove scraper repo
rm -rf ~/ydun-scraper

# Reset git
cd ~/dev-network
git checkout beast/

# Remove .env
rm beast/docker/.env
```

**Time to Rollback:** 5 minutes

---

## Success Metrics

**Deployment Success:**
- ✅ 7 Docker containers running (6 monitoring + 1 scraper)
- ✅ Prometheus collecting from 3 targets
- ✅ Grafana showing dashboards with live data
- ✅ Portainer managing all containers
- ✅ Cloudflare Tunnel HEALTHY
- ✅ All 3 HTTPS endpoints accessible externally
- ✅ Ydun scraper functional and responding

**Operational Success:**
- ✅ Services auto-restart on failure
- ✅ Metrics retained for 30 days
- ✅ External access secured via Cloudflare
- ✅ Scraper ready for Mundus integration
- ✅ Complete documentation available

---

## Next Steps After Deployment

1. **Mundus Integration:**
   - Update Mundus Supabase edge function
   - Change scraper URL to: https://scrape.kitt.agency/scrape
   - Test end-to-end: Mundus → Beast scraper

2. **Load Testing:**
   - Monitor Grafana during Mundus testing
   - Watch ydun-scraper resource usage
   - Verify scraper handles concurrent requests
   - Document performance baseline

3. **Future Enhancements:**
   - Add Prometheus metrics endpoint to scraper (/metrics)
   - Configure Grafana alerts for scraper errors
   - Add rate limiting if needed
   - Scale scraper horizontally if load requires

---

**Document Status**: Ready for Execution
**Next Step**: Begin Phase 1, Step 1.1 (Clone ydun-scraper)
**Execution Mode**: Autonomous (YOLO) with checkpoints

---

**This document follows Jimmy's Workflow (Red/Green Checkpoint System v1.1)**

**Last Updated**: 2025-10-17

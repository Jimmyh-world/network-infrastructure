# Beast Monitoring Infrastructure Setup

**Created**: 2025-10-17
**Machine**: Beast (thebeast - 192.168.68.100)
**Workflow**: RED/GREEN/CHECKPOINT (Jimmy's Workflow v1.1)
**Status**: Planning Phase

---

## Overview

This document defines the complete RED/GREEN/CHECKPOINT workflow for deploying a production-grade monitoring stack on Beast with external HTTPS access via Cloudflare Tunnel.

### Infrastructure Components

**Monitoring Stack:**
- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization and dashboards
- **Node Exporter** - Beast system metrics (CPU, RAM, disk, network)
- **cAdvisor** - Docker container metrics

**Management:**
- **Portainer** - Docker GUI management interface

**External Access:**
- **Cloudflare Tunnel** - Secure HTTPS access without port forwarding

### Success Criteria

- ✅ All services running in Docker
- ✅ Prometheus collecting metrics from Node Exporter and cAdvisor
- ✅ Grafana dashboards displaying system and container metrics
- ✅ Cloudflare Tunnel providing secure HTTPS access
- ✅ All services auto-start on Beast reboot
- ✅ Complete rollback procedures documented

---

## Workflow Phases

1. **Phase 1**: Docker Network & Base Configuration
2. **Phase 2**: Prometheus + Node Exporter + cAdvisor
3. **Phase 3**: Grafana Setup
4. **Phase 4**: Portainer Setup
5. **Phase 5**: Cloudflare Tunnel Configuration
6. **Phase 6**: End-to-End Integration Test

---

## Phase 1: Docker Network & Base Configuration

### Step 1.1: Create Docker Compose Base Structure

🔴 **IMPLEMENT:**
- Create `beast/docker/docker-compose.yml` with networks and volumes
- Define shared network: `monitoring`
- Define volumes: `prometheus-data`, `grafana-data`, `portainer-data`
- Set up base configuration structure
- Complexity: 🟢 Simple
- Estimated: 10 minutes
- Files to create:
  - `beast/docker/docker-compose.yml`
  - `beast/docker/.env.example`

🟢 **VALIDATE:**
- Run: `cd ~/dev-network/beast/docker && docker compose config` (expect: valid YAML, no errors)
- Check: Networks defined correctly
- Check: Volumes defined correctly
- Verify: No syntax errors in docker-compose.yml

🔵 **CHECKPOINT:** Docker Compose Base Structure Created
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 10 minutes
**Actual**: [TBD]
**Tests**: docker compose config validation
**Rollback**: `rm -rf ~/dev-network/beast/docker/*`
**Dependencies**: None
**Blockers**: None
**Notes**: Base structure only, no services yet

---

## Phase 2: Prometheus + Node Exporter + cAdvisor

### Step 2.1: Create Prometheus Configuration

🔴 **IMPLEMENT:**
- Create `beast/monitoring/prometheus/prometheus.yml`
- Configure scrape targets:
  - Prometheus self-monitoring (localhost:9090)
  - Node Exporter (node-exporter:9100)
  - cAdvisor (cadvisor:8080)
- Set scrape interval: 15s
- Set retention: 30d
- Complexity: 🟡 Moderate
- Estimated: 15 minutes
- Files to create:
  - `beast/monitoring/prometheus/prometheus.yml`

🟢 **VALIDATE:**
- Check: YAML syntax valid: `yamllint beast/monitoring/prometheus/prometheus.yml` (or manual review)
- Verify: All scrape targets defined
- Verify: Scrape intervals configured
- Check: No placeholder values remain

🔵 **CHECKPOINT:** Prometheus Configuration Created
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 15 minutes
**Actual**: [TBD]
**Tests**: YAML validation
**Rollback**: `rm beast/monitoring/prometheus/prometheus.yml`
**Dependencies**: Step 1.1 (COMPLETE)
**Blockers**: None

---

### Step 2.2: Add Prometheus, Node Exporter, cAdvisor to Docker Compose

🔴 **IMPLEMENT:**
- Add Prometheus service to docker-compose.yml
  - Image: prom/prometheus:latest
  - Port: 9090:9090
  - Volume: prometheus config + data
  - Network: monitoring
- Add Node Exporter service
  - Image: prom/node-exporter:latest
  - Port: 9100:9100
  - Host metrics access
  - Network: monitoring
- Add cAdvisor service
  - Image: gcr.io/cadvisor/cadvisor:latest
  - Port: 8080:8080
  - Docker socket access
  - Network: monitoring
- Complexity: 🟡 Moderate
- Estimated: 20 minutes
- Files to modify:
  - `beast/docker/docker-compose.yml`

🟢 **VALIDATE:**
- Run: `docker compose config` (expect: valid configuration)
- Run: `docker compose up -d prometheus node-exporter cadvisor`
- Run: `docker ps` (expect: 3 containers running)
- Run: `curl http://localhost:9090/-/healthy` (expect: Prometheus is Healthy)
- Run: `curl http://localhost:9100/metrics` (expect: node metrics returned)
- Run: `curl http://localhost:8080/healthz` (expect: ok)
- Check: `docker logs prometheus` (expect: no errors, targets discovered)
- Check: `docker logs node-exporter` (expect: running, no errors)
- Check: `docker logs cadvisor` (expect: running, no errors)
- Browse: http://192.168.68.100:9090/targets (expect: all targets UP)

🔵 **CHECKPOINT:** Prometheus Stack Deployed
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 20 minutes
**Actual**: [TBD]
**Tests**: ✅ HTTP health checks, ✅ Docker logs clean, ✅ Targets UP
**Build**: N/A (Docker deployment)
**Rollback**:
```bash
cd ~/dev-network/beast/docker
docker compose down prometheus node-exporter cadvisor
docker volume rm beast_prometheus-data
git checkout beast/docker/docker-compose.yml
```
**Dependencies**: Steps 1.1, 2.1 (COMPLETE)
**Blockers**: None
**Notes**: Prometheus must discover all 3 targets (self, node-exporter, cadvisor)

---

## Phase 3: Grafana Setup

### Step 3.1: Add Grafana to Docker Compose

🔴 **IMPLEMENT:**
- Add Grafana service to docker-compose.yml
  - Image: grafana/grafana:latest
  - Port: 3000:3000
  - Volume: grafana-data (persistent dashboards)
  - Environment variables:
    - GF_SECURITY_ADMIN_PASSWORD (from .env)
    - GF_SERVER_ROOT_URL
    - GF_INSTALL_PLUGINS (if needed)
  - Network: monitoring
- Create `.env` file with secrets
- Complexity: 🟡 Moderate
- Estimated: 15 minutes
- Files to modify:
  - `beast/docker/docker-compose.yml`
  - `beast/docker/.env` (create from .env.example)

🟢 **VALIDATE:**
- Run: `docker compose config` (expect: valid, env vars loaded)
- Run: `docker compose up -d grafana`
- Run: `docker ps | grep grafana` (expect: running)
- Run: `curl http://localhost:3000/api/health` (expect: {"database":"ok"})
- Check: `docker logs grafana` (expect: HTTP Server Listen, no errors)
- Browse: http://192.168.68.100:3000 (expect: login page)
- Test: Login with admin credentials from .env (expect: success)

🔵 **CHECKPOINT:** Grafana Deployed
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 15 minutes
**Actual**: [TBD]
**Tests**: ✅ HTTP health check, ✅ Login successful
**Rollback**:
```bash
docker compose down grafana
docker volume rm beast_grafana-data
git checkout beast/docker/docker-compose.yml beast/docker/.env
```
**Dependencies**: Step 1.1 (COMPLETE)
**Blockers**: None
**Notes**: Verify .env not committed to git (check .gitignore)

---

### Step 3.2: Configure Prometheus Data Source in Grafana

🔴 **IMPLEMENT:**
- Create provisioning config: `beast/monitoring/grafana/provisioning/datasources/prometheus.yml`
- Configure Prometheus datasource:
  - URL: http://prometheus:9090
  - Access: proxy
  - Default: true
- Update docker-compose.yml to mount provisioning directory
- Complexity: 🟡 Moderate
- Estimated: 15 minutes
- Files to create:
  - `beast/monitoring/grafana/provisioning/datasources/prometheus.yml`
- Files to modify:
  - `beast/docker/docker-compose.yml` (add volume mount)

🟢 **VALIDATE:**
- Run: `docker compose restart grafana`
- Check: `docker logs grafana | grep -i datasource` (expect: datasource loaded)
- Browse: Grafana → Configuration → Data Sources
- Verify: Prometheus datasource exists and is default
- Test: Click "Test" button (expect: "Data source is working")
- Query: Run test query in Explore: `up` (expect: metrics returned)

🔵 **CHECKPOINT:** Grafana Connected to Prometheus
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 15 minutes
**Actual**: [TBD]
**Tests**: ✅ Datasource test passed, ✅ Query returns metrics
**Rollback**:
```bash
rm -rf beast/monitoring/grafana/
git checkout beast/docker/docker-compose.yml
docker compose restart grafana
```
**Dependencies**: Steps 2.2, 3.1 (COMPLETE)
**Blockers**: None
**Notes**: Prometheus must be reachable via Docker network

---

### Step 3.3: Import System Monitoring Dashboards

🔴 **IMPLEMENT:**
- Download and configure dashboard JSON files:
  - Node Exporter Full (Dashboard ID: 1860)
  - Docker Container Monitoring (Dashboard ID: 193)
- Save to `beast/monitoring/grafana/dashboards/`
- Create dashboard provisioning config
- Update docker-compose.yml to mount dashboards directory
- Complexity: 🟢 Simple
- Estimated: 20 minutes
- Files to create:
  - `beast/monitoring/grafana/provisioning/dashboards/default.yml`
  - `beast/monitoring/grafana/dashboards/node-exporter-full.json`
  - `beast/monitoring/grafana/dashboards/docker-containers.json`
- Files to modify:
  - `beast/docker/docker-compose.yml` (add volume mount)

🟢 **VALIDATE:**
- Run: `docker compose restart grafana`
- Check: `docker logs grafana | grep -i dashboard` (expect: dashboards loaded)
- Browse: Grafana → Dashboards
- Verify: "Node Exporter Full" dashboard exists
- Verify: "Docker Containers" dashboard exists
- Test: Open "Node Exporter Full" (expect: system metrics displayed)
- Test: Open "Docker Containers" (expect: container metrics displayed)
- Check: All panels show data (no "No Data" errors)

🔵 **CHECKPOINT:** Grafana Dashboards Configured
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 20 minutes
**Actual**: [TBD]
**Tests**: ✅ Dashboards loaded, ✅ Metrics displayed
**Rollback**:
```bash
rm -rf beast/monitoring/grafana/dashboards/
rm beast/monitoring/grafana/provisioning/dashboards/default.yml
git checkout beast/docker/docker-compose.yml
docker compose restart grafana
```
**Dependencies**: Step 3.2 (COMPLETE)
**Blockers**: None
**Notes**: Dashboards should auto-load on Grafana restart

---

## Phase 4: Portainer Setup

### Step 4.1: Add Portainer to Docker Compose

🔴 **IMPLEMENT:**
- Add Portainer service to docker-compose.yml
  - Image: portainer/portainer-ce:latest
  - Port: 9443:9443 (HTTPS) and 8000:8000 (edge agent)
  - Volume: portainer-data + Docker socket
  - Network: monitoring
  - Restart: always
- Complexity: 🟢 Simple
- Estimated: 10 minutes
- Files to modify:
  - `beast/docker/docker-compose.yml`

🟢 **VALIDATE:**
- Run: `docker compose config` (expect: valid)
- Run: `docker compose up -d portainer`
- Run: `docker ps | grep portainer` (expect: running)
- Check: `docker logs portainer` (expect: starting, no errors)
- Browse: https://192.168.68.100:9443 (expect: initial setup page)
- Test: Create admin account (expect: success)
- Test: Connect to local Docker environment (expect: containers visible)
- Verify: Can see prometheus, grafana, node-exporter, cadvisor containers

🔵 **CHECKPOINT:** Portainer Deployed
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 10 minutes
**Actual**: [TBD]
**Tests**: ✅ HTTPS accessible, ✅ Admin account created, ✅ Containers visible
**Rollback**:
```bash
docker compose down portainer
docker volume rm beast_portainer-data
git checkout beast/docker/docker-compose.yml
```
**Dependencies**: Step 1.1 (COMPLETE)
**Blockers**: None
**Notes**: Initial admin password must be set within 5 minutes of first start

---

## Phase 5: Cloudflare Tunnel Configuration

### Step 5.1: Install Cloudflare Tunnel CLI on Beast

🔴 **IMPLEMENT:**
- Install cloudflared on Beast host (not Docker, for initial setup)
- Authenticate with Cloudflare account
- Create tunnel: `beast-tunnel`
- Store tunnel credentials in `beast/cloudflare/`
- Complexity: 🟡 Moderate
- Estimated: 15 minutes
- Commands:
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create beast-tunnel

# Copy credentials
cp ~/.cloudflared/*.json ~/dev-network/beast/cloudflare/tunnel-credentials.json
```

🟢 **VALIDATE:**
- Run: `cloudflared --version` (expect: version displayed)
- Run: `cloudflared tunnel list` (expect: beast-tunnel listed)
- Check: `ls ~/dev-network/beast/cloudflare/` (expect: tunnel-credentials.json exists)
- Verify: Credentials file is valid JSON
- Check: Tunnel UUID matches credentials file

🔵 **CHECKPOINT:** Cloudflare Tunnel Authenticated
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 15 minutes
**Actual**: [TBD]
**Tests**: ✅ Tunnel created, ✅ Credentials stored
**Rollback**:
```bash
cloudflared tunnel delete beast-tunnel
rm ~/dev-network/beast/cloudflare/tunnel-credentials.json
sudo apt remove cloudflared
```
**Dependencies**: None (external Cloudflare service)
**Blockers**: Requires Cloudflare account access
**Notes**: Tunnel credentials are secrets - ensure .gitignore covers them

---

### Step 5.2: Configure Cloudflare Tunnel Routing

🔴 **IMPLEMENT:**
- Create tunnel config: `beast/cloudflare/config.yml`
- Configure routes:
  - `grafana.yourdomain.com` → http://localhost:3000
  - `portainer.yourdomain.com` → https://localhost:9443
  - Future: `ydun.yourdomain.com` → http://localhost:8080 (placeholder)
- Create DNS records via cloudflared
- Complexity: 🟡 Moderate
- Estimated: 20 minutes
- Files to create:
  - `beast/cloudflare/config.yml`
- Commands:
```bash
# Create DNS routes
cloudflared tunnel route dns beast-tunnel grafana.yourdomain.com
cloudflared tunnel route dns beast-tunnel portainer.yourdomain.com
```

🟢 **VALIDATE:**
- Run: `cloudflared tunnel route list` (expect: 2+ routes configured)
- Check: `cat beast/cloudflare/config.yml` (expect: valid YAML, all routes defined)
- Verify: DNS records created in Cloudflare dashboard
- Query: `nslookup grafana.yourdomain.com` (expect: CNAME to tunnel)
- Query: `nslookup portainer.yourdomain.com` (expect: CNAME to tunnel)

🔵 **CHECKPOINT:** Tunnel Routes Configured
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 20 minutes
**Actual**: [TBD]
**Tests**: ✅ DNS records created, ✅ Config valid
**Rollback**:
```bash
cloudflared tunnel route delete grafana.yourdomain.com
cloudflared tunnel route delete portainer.yourdomain.com
rm beast/cloudflare/config.yml
```
**Dependencies**: Step 5.1 (COMPLETE)
**Blockers**: Requires domain selection
**Notes**: Replace yourdomain.com with actual domain from available 40

---

### Step 5.3: Add Cloudflare Tunnel to Docker Compose

🔴 **IMPLEMENT:**
- Add cloudflared service to docker-compose.yml
  - Image: cloudflare/cloudflared:latest
  - Command: tunnel run
  - Volume: mount config.yml and tunnel-credentials.json
  - Network: monitoring (to access services)
  - Restart: always
- Complexity: 🟡 Moderate
- Estimated: 15 minutes
- Files to modify:
  - `beast/docker/docker-compose.yml`

🟢 **VALIDATE:**
- Run: `docker compose config` (expect: valid)
- Run: `docker compose up -d cloudflared`
- Run: `docker ps | grep cloudflared` (expect: running)
- Check: `docker logs cloudflared` (expect: tunnel connected, no errors)
- Check: Cloudflare dashboard → Traffic → Tunnel (expect: beast-tunnel HEALTHY)
- Test: `curl https://grafana.yourdomain.com` (expect: Grafana login page via HTTPS)
- Test: `curl https://portainer.yourdomain.com` (expect: Portainer login page via HTTPS)

🔵 **CHECKPOINT:** Cloudflare Tunnel Deployed in Docker
**Status**: PENDING
**Complexity**: 🟡 Moderate
**Estimated**: 15 minutes
**Actual**: [TBD]
**Tests**: ✅ Tunnel running, ✅ HTTPS access working
**Rollback**:
```bash
docker compose down cloudflared
git checkout beast/docker/docker-compose.yml
```
**Dependencies**: Steps 3.1, 4.1, 5.2 (COMPLETE)
**Blockers**: None
**Notes**: Tunnel must be HEALTHY in Cloudflare dashboard before proceeding

---

## Phase 6: End-to-End Integration Test

### Step 6.1: Full Stack Validation

🔴 **IMPLEMENT:**
- No changes - validation only
- Test all services together
- Verify external HTTPS access
- Verify metrics collection end-to-end
- Complexity: 🟢 Simple (testing only)
- Estimated: 20 minutes

🟢 **VALIDATE:**

**Docker Health:**
- Run: `cd ~/dev-network/beast/docker && docker compose ps` (expect: all services UP)
- Run: `docker stats --no-stream` (expect: resource usage displayed)
- Check: All containers healthy, no restart loops

**Metrics Collection:**
- Browse: http://192.168.68.100:9090/targets (expect: all targets UP and healthy)
- Query: Prometheus → `up` (expect: all exporters returning 1)
- Query: Prometheus → `node_memory_MemAvailable_bytes` (expect: Beast RAM data)
- Query: Prometheus → `container_memory_usage_bytes` (expect: container metrics)

**Grafana Dashboards:**
- Browse: https://grafana.yourdomain.com (expect: accessible via HTTPS)
- Login: Use credentials from .env (expect: success)
- Dashboard: "Node Exporter Full" (expect: all panels showing data)
- Dashboard: "Docker Containers" (expect: prometheus, grafana, etc. visible)
- Check: No "No Data" errors in any panel
- Check: Data updating in real-time (refresh dashboard)

**Portainer Management:**
- Browse: https://portainer.yourdomain.com (expect: accessible via HTTPS)
- Login: Use admin account (expect: success)
- Check: All 6 containers visible (prometheus, grafana, node-exporter, cadvisor, portainer, cloudflared)
- Check: Container stats displaying
- Test: Restart grafana container via Portainer (expect: success, no downtime)

**External HTTPS Access:**
- Test from external network (mobile hotspot):
  - `curl -I https://grafana.yourdomain.com` (expect: 200 OK)
  - `curl -I https://portainer.yourdomain.com` (expect: 200 OK)
- Verify: No certificate warnings
- Verify: Cloudflare proxy working

**Auto-Start on Reboot:**
- Document: `docker compose` services have `restart: unless-stopped`
- Plan reboot test: Schedule for later verification

**Security Checks:**
- Check: `.env` file NOT in git: `git status` (expect: not listed)
- Check: `tunnel-credentials.json` NOT in git: `git status` (expect: not listed)
- Check: `.gitignore` contains `.env` and `tunnel-credentials.json`
- Verify: Only HTTPS access exposed externally (no direct port 9090/3000/9443 access)

🔵 **CHECKPOINT:** Complete Infrastructure Validated
**Status**: PENDING
**Complexity**: 🟢 Simple (validation only)
**Estimated**: 20 minutes
**Actual**: [TBD]
**Tests**: ✅ All services healthy, ✅ Metrics flowing, ✅ Dashboards working, ✅ External HTTPS access working
**Rollback**: Full teardown:
```bash
cd ~/dev-network/beast/docker
docker compose down -v
rm -rf ~/dev-network/beast/
cloudflared tunnel delete beast-tunnel
```
**Dependencies**: All previous steps (COMPLETE)
**Blockers**: None
**Notes**: This is the final validation - all components must work together

---

### Step 6.2: Documentation and Handoff

🔴 **IMPLEMENT:**
- Create `beast/docs/MONITORING-OPERATIONS.md` with:
  - Service URLs (internal and external)
  - Common operations (start, stop, restart, logs)
  - Troubleshooting guide
  - Backup procedures
  - Dashboard import instructions
  - Adding new metrics sources
- Update main README.md with Beast monitoring section
- Create `beast/docs/ROLLBACK-PROCEDURES.md`
- Complexity: 🟢 Simple (documentation only)
- Estimated: 30 minutes
- Files to create:
  - `beast/docs/MONITORING-OPERATIONS.md`
  - `beast/docs/ROLLBACK-PROCEDURES.md`
- Files to modify:
  - `README.md` (add Beast section)

🟢 **VALIDATE:**
- Check: All docs are markdown formatted
- Check: All commands are copy-paste ready
- Check: All URLs are correct (replace placeholders)
- Verify: Rollback procedures are complete and tested
- Review: Documentation is clear and factual (no AI fluff)

🔵 **CHECKPOINT:** Documentation Complete
**Status**: PENDING
**Complexity**: 🟢 Simple
**Estimated**: 30 minutes
**Actual**: [TBD]
**Tests**: ✅ Docs reviewed, ✅ Commands validated
**Rollback**: N/A (documentation only)
**Dependencies**: Step 6.1 (COMPLETE)
**Blockers**: None
**Notes**: Follow AGENTS.md documentation standards

---

## Pre-Execution Checklist

Before starting Phase 1, verify:

- [ ] Beast is accessible: `ssh jimmyb@192.168.68.100`
- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker compose version`
- [ ] Git repository initialized: `git status`
- [ ] Cloudflare account accessible
- [ ] Domain selected for tunnel endpoints
- [ ] Sufficient disk space: `df -h` (expect: >20GB free)
- [ ] This workflow document reviewed and understood

## Rollback Strategy

**Per-Phase Rollback**: See individual checkpoint rollback commands

**Full Stack Rollback**:
```bash
# Stop all services
cd ~/dev-network/beast/docker
docker compose down -v

# Remove all data volumes
docker volume rm beast_prometheus-data beast_grafana-data beast_portainer-data

# Delete Cloudflare tunnel
cloudflared tunnel delete beast-tunnel

# Remove configuration files
cd ~/dev-network
git checkout beast/
# Or: rm -rf beast/
```

**Time to Rollback**: < 5 minutes

---

## Success Metrics

**Deployment Success:**
- ✅ All 6 Docker containers running
- ✅ Prometheus collecting from 3 targets
- ✅ Grafana showing 2 dashboards with data
- ✅ External HTTPS access working for Grafana and Portainer
- ✅ Cloudflare Tunnel HEALTHY

**Operational Success:**
- ✅ Services auto-restart on reboot
- ✅ Metrics retained for 30 days
- ✅ Zero manual intervention required
- ✅ Complete documentation available

---

## Notes

**Estimated Total Time**: 3-4 hours (including validation)

**Complexity Breakdown**:
- 🟢 Simple: 5 steps
- 🟡 Moderate: 8 steps
- 🔴 Complex: 0 steps

**Dependencies**: External services (Cloudflare) may impact timeline

**Security**: Ensure all secrets (.env, tunnel credentials) are in .gitignore

**Future Enhancements**:
- Alerting (Alertmanager)
- Log aggregation (Loki)
- Uptime monitoring (Blackbox Exporter)
- Guardian Pi integration

---

**Document Status**: Ready for Execution
**Next Step**: Begin Phase 1, Step 1.1
**Execution Mode**: Manual (step-by-step with human approval at each checkpoint)

---

**This document follows Jimmy's Workflow (Red/Green Checkpoint System v1.1)**

**Last Updated**: 2025-10-17

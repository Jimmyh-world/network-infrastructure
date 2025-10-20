# Infrastructure Optimization Plan

**Created:** 2025-10-20
**Status:** Planning Complete - Ready for Execution
**Purpose:** Make Mundus staging infrastructure production-ready
**Context:** Stage 1 (tracer bullet) complete, optimizing before Stage 2

---

## Overview

After successful Stage 1 deployment, the infrastructure needs optimization for:
- **Reliability:** Auto-restart services, survive reboots
- **Automation:** Push to GitHub → auto-deploy
- **Visibility:** Monitor all services, catch issues early
- **Debugging:** Centralized logs across services

**Current State:** Manual, fragile (requires human intervention)
**Target State:** Automated, robust (self-healing, monitored)

---

## Optimization Roadmap

| Priority | Optimization | Time | Complexity | Impact |
|----------|-------------|------|------------|--------|
| **1** | systemd for Cloudflare Tunnel | 15 min | 🟢 Simple | High |
| **2** | Webhook Auto-Deploy (Vault) | 45 min | 🟡 Moderate | High |
| **3** | Container Monitoring | 30 min | 🟡 Moderate | Medium |
| **4** | Log Aggregation (Loki) | 45 min | 🟡 Moderate | Medium |

**Total for 1-3:** ~90 minutes
**Total for all:** ~2.5 hours

---

## Optimization 1: systemd Service for Cloudflare Tunnel

### Current Problem

```bash
# Manual start (doesn't survive reboot)
nohup cloudflared tunnel --config config.yml run > /tmp/log 2>&1 &

# Issues:
- Doesn't restart if crashes
- Doesn't start on Beast reboot
- Manual PID tracking
- No standard log rotation
```

### Solution: systemd Service

**Benefits:**
- ✅ Auto-restart on failure
- ✅ Auto-start on boot
- ✅ Integrated logging (journalctl)
- ✅ Standard Linux service management
- ✅ Proper process supervision

### Implementation Steps

**1. Create service files (2 files needed)**

**File:** `/etc/systemd/system/cloudflared-kitt.service`
```ini
[Unit]
Description=Cloudflare Tunnel - kitt.agency
After=network.target

[Service]
Type=simple
User=jimmyb
ExecStart=/usr/local/bin/cloudflared tunnel --config /home/jimmyb/dev-network/beast/cloudflare/config.yml run
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**File:** `/etc/systemd/system/cloudflared-mundus.service`
```ini
[Unit]
Description=Cloudflare Tunnel - mundus (web3studio.dev)
After=network.target

[Service]
Type=simple
User=jimmyb
ExecStart=/usr/local/bin/cloudflared tunnel --config /home/jimmyb/dev-network/beast/cloudflare/config-web3studio.yml run
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**2. Install and enable services**

```bash
# Stop manual processes
pkill -f "cloudflared tunnel"

# Copy service files
sudo cp /home/jimmyb/dev-network/beast/systemd/cloudflared-kitt.service /etc/systemd/system/
sudo cp /home/jimmyb/dev-network/beast/systemd/cloudflared-mundus.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services (auto-start on boot)
sudo systemctl enable cloudflared-kitt
sudo systemctl enable cloudflared-mundus

# Start services
sudo systemctl start cloudflared-kitt
sudo systemctl start cloudflared-mundus

# Check status
sudo systemctl status cloudflared-kitt
sudo systemctl status cloudflared-mundus
```

**3. Verify operation**

```bash
# Check services are running
systemctl is-active cloudflared-kitt
systemctl is-active cloudflared-mundus
# Expected: active

# View logs
journalctl -u cloudflared-kitt -f
journalctl -u cloudflared-mundus -f

# Test endpoints
curl https://grafana.kitt.agency/api/health
curl https://mundus.web3studio.dev/api/health
```

### Management Commands

```bash
# Start/stop/restart
sudo systemctl start cloudflared-kitt
sudo systemctl stop cloudflared-kitt
sudo systemctl restart cloudflared-kitt

# View status
sudo systemctl status cloudflared-kitt

# View logs (last 100 lines)
journalctl -u cloudflared-kitt -n 100

# Follow logs in real-time
journalctl -u cloudflared-kitt -f

# View logs since boot
journalctl -u cloudflared-kitt -b
```

### Rollback

```bash
# Stop and disable services
sudo systemctl stop cloudflared-kitt cloudflared-mundus
sudo systemctl disable cloudflared-kitt cloudflared-mundus

# Remove service files
sudo rm /etc/systemd/system/cloudflared-kitt.service
sudo rm /etc/systemd/system/cloudflared-mundus.service

# Reload systemd
sudo systemctl daemon-reload

# Start manual processes (old way)
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
nohup cloudflared tunnel --config cloudflare/config-web3studio.yml run > /tmp/cloudflared-mundus.log 2>&1 &
```

**Estimated Time:** 15 minutes
**Complexity:** 🟢 Simple
**Risk:** Low (easy rollback)

---

## Optimization 2: Webhook Auto-Deploy with Vault Integration

**See:** `docs/WEBHOOK-VAULT-INTEGRATION.md` for complete implementation

### Summary

**Current State:** Manual deploy
```
1. Push to GitHub
2. SSH to Beast
3. git pull
4. docker compose build
5. docker compose up -d
```

**Target State:** Automated deploy
```
1. Push to GitHub → DONE
   (GitHub webhook triggers Beast automatically)
```

### Key Features

- **Instant:** Deploy triggered immediately on push
- **Secure:** GitHub signature verification
- **Vault-backed:** Webhook secret stored in Vault (not .env)
- **Safe:** Only deploys main branch
- **Logged:** All deployments audited

### Components

1. **Webhook receiver service** (Node.js Express)
2. **Vault secret storage** (webhook_secret)
3. **GitHub webhook configuration**
4. **Cloudflare Tunnel route** (webhook.mundus.web3studio.dev)

**Estimated Time:** 45 minutes
**Complexity:** 🟡 Moderate
**Risk:** Medium (can disable webhook if issues)

---

## Optimization 3: Container Monitoring

### Current Problem

```bash
# Only manual checks
docker compose ps
docker stats
docker compose logs
```

No visibility into:
- Container resource trends over time
- Performance degradation
- Early warning signs
- Historical data

### Solution: Prometheus + Grafana Dashboards

**What You'll See:**
- CPU usage per container (chart over time)
- Memory usage trends
- HTTP request rates
- Response times
- Container restarts (alert on failures)
- Disk I/O
- Network traffic

### Implementation Steps

**1. Add cAdvisor metrics to Prometheus** (already collecting)

Verify Prometheus is scraping cAdvisor:
```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="cadvisor")'
```

**2. Import Grafana dashboards**

**Dashboard 1: Docker Container Overview**
- Dashboard ID: 193
- Source: https://grafana.com/grafana/dashboards/193

**Dashboard 2: Mundus Service Metrics** (custom)
- HTTP request rate
- Response times
- Error rates
- Active connections

**Steps:**
```bash
# Access Grafana
# Browser: https://grafana.kitt.agency

# Import dashboard
1. Click + → Import
2. Enter ID: 193
3. Select Prometheus data source
4. Click Import

# Repeat for custom Mundus dashboard
1. Click + → Create → Dashboard
2. Add panels for:
   - HTTP request rate (counter query)
   - Response times (histogram query)
   - Container CPU/memory (cAdvisor metrics)
3. Save as "Mundus Service Metrics"
```

**3. Configure alerts** (optional)

Alert conditions:
- Container CPU >80% for 5 minutes
- Container memory >80%
- Container restarted (restart count increased)
- HTTP error rate >5%

**4. Test**

```bash
# Generate load
for i in {1..100}; do
  curl https://mundus.web3studio.dev/api/health
done

# Check Grafana dashboard shows traffic spike
```

### Available Metrics

**From cAdvisor:**
```
container_cpu_usage_seconds_total
container_memory_usage_bytes
container_network_receive_bytes_total
container_network_transmit_bytes_total
container_fs_reads_bytes_total
container_fs_writes_bytes_total
```

**Custom (future):**
```
mundus_http_requests_total{path="/api/health"}
mundus_http_request_duration_seconds
mundus_active_connections
```

**Estimated Time:** 30 minutes
**Complexity:** 🟡 Moderate
**Risk:** Low (read-only, doesn't affect services)

---

## Optimization 4: Log Aggregation (Loki)

### Current Problem

```bash
# Logs scattered across containers
docker compose logs hello-world
docker compose logs backend     # (future)
docker compose logs editor      # (future)

# Issues:
- Must check each container individually
- Logs lost when container recreated
- Can't search across all services
- Can't correlate logs with metrics
```

### Solution: Grafana Loki

**What You'll Get:**
- All logs in one place (Grafana UI)
- Search across all services at once
- Correlate logs with metrics
- Retain logs even after container restart
- Alert on log patterns

### Implementation Steps

**1. Add Loki + Promtail to docker-compose**

```yaml
# beast/docker/docker-compose.yml
services:
  loki:
    image: grafana/loki:latest
    container_name: loki
    restart: unless-stopped
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki
      - ../monitoring/loki/loki-config.yml:/etc/loki/local-config.yaml
    networks:
      - monitoring

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    restart: unless-stopped
    volumes:
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ../monitoring/promtail/promtail-config.yml:/etc/promtail/config.yml
    networks:
      - monitoring

volumes:
  loki-data:
    driver: local
```

**2. Create Loki config**

**File:** `beast/monitoring/loki/loki-config.yml`
```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: false
  retention_period: 0s
```

**3. Create Promtail config**

**File:** `beast/monitoring/promtail/promtail-config.yml`
```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    static_configs:
      - targets:
          - localhost
        labels:
          job: docker
          __path__: /var/lib/docker/containers/*/*-json.log
```

**4. Configure Grafana to use Loki**

```bash
# Access Grafana
# Browser: https://grafana.kitt.agency

# Add Loki data source
1. Configuration → Data Sources → Add data source
2. Select Loki
3. URL: http://loki:3100
4. Click Save & Test
```

**5. Query logs in Grafana**

```
# All logs from mundus container
{container_name="mundus-hello-world"}

# Error logs only
{container_name="mundus-hello-world"} |= "error"

# Last 1 hour
{container_name="mundus-hello-world"} [1h]

# Combined with metrics (in dashboard)
- Panel 1: Request rate (Prometheus metric)
- Panel 2: Error logs (Loki logs)
```

### Benefits

- ✅ Search "error" across ALL containers instantly
- ✅ Logs retained even if container deleted
- ✅ Correlate logs + metrics in one dashboard
- ✅ Alert on log patterns ("too many errors")
- ✅ Export logs for analysis

**Estimated Time:** 45 minutes
**Complexity:** 🟡 Moderate
**Risk:** Low (only reads logs, doesn't affect services)

---

## Execution Order

### Recommended: Sequential

**Session 1: Reliability (15 min)**
1. systemd for tunnels
2. Test reboot survivability

**Session 2: Automation (45 min)**
1. Webhook with Vault
2. Test push → auto-deploy

**Session 3: Visibility (75 min)**
1. Container monitoring (30 min)
2. Log aggregation (45 min)
3. Create dashboards

### Alternative: All at Once (90 min)

Execute optimizations 1-3 in one session, skip log aggregation until Stage 2 (when multiple services benefit more from centralized logs).

---

## Success Criteria

**After Optimization 1:**
- ✅ `sudo reboot` → tunnels auto-start
- ✅ `systemctl status cloudflared-kitt` → active
- ✅ Services accessible after reboot without manual intervention

**After Optimization 2:**
- ✅ Push to GitHub → Beast deploys automatically (~2 min)
- ✅ No SSH required
- ✅ Webhook secret stored in Vault
- ✅ GitHub shows successful webhook delivery

**After Optimization 3:**
- ✅ Grafana dashboard shows all container metrics
- ✅ Can see CPU/memory trends over time
- ✅ Alerts fire when thresholds exceeded

**After Optimization 4:**
- ✅ Can search logs across all containers
- ✅ Logs retained after container restart
- ✅ Can correlate logs + metrics in dashboards

---

## Rollback Procedures

**Optimization 1:**
- Disable systemd services
- Return to manual nohup commands

**Optimization 2:**
- Disable webhook in GitHub
- Return to manual git pull + build

**Optimization 3:**
- No rollback needed (dashboards are read-only)
- Just delete dashboards if not useful

**Optimization 4:**
- Remove Loki/Promtail from docker-compose
- Logs still available via `docker compose logs`

---

## Resource Impact

| Optimization | RAM | CPU | Disk | Network |
|-------------|-----|-----|------|---------|
| systemd (1) | 0 | 0 | 0 | 0 |
| webhook (2) | +50MB | <1% | Negligible | Minimal |
| monitoring (3) | 0 (already running) | 0 | 0 | 0 |
| logs (4) | +150MB | <2% | +500MB/week | Minimal |

**Total New Resources:** ~200MB RAM, <3% CPU, ~2GB disk/month

**Available on Beast:** 95GB RAM, 1.99TB disk → Plenty of headroom

---

## Dependencies

**Prerequisites:**
- ✅ Stage 1 complete (tracer bullet deployed)
- ✅ Vault operational (for optimization 2)
- ✅ Prometheus + Grafana running (for optimizations 3 & 4)
- ✅ GitHub repo configured (for optimization 2)

**Blockers:** None - all prerequisites met

---

## Next Steps

**To Execute This Plan:**

1. **Review this document** - Understand each optimization
2. **Choose approach** - Sequential or all-at-once
3. **Follow Jimmy's Workflow** - RED/GREEN/CHECKPOINT for each
4. **Use detailed guides:**
   - `docs/WEBHOOK-VAULT-INTEGRATION.md` for optimization 2
   - Beast execution specs (create as needed)
5. **Test thoroughly** before marking complete
6. **Update NEXT-SESSION-START-HERE.md** when done

---

**Document Status:** Planning Complete - Ready for Execution
**Created:** 2025-10-20
**Estimated Total Time:** 90 minutes (optimizations 1-3) or 2.5 hours (all 4)

# Monitoring Infrastructure Validation Procedures

**Document**: Full Stack Validation & Testing
**Date Created**: 2025-10-17
**Phase**: 6, Step 6.1

---

## Pre-Deployment Validation Checklist

Before starting the services, verify the infrastructure is properly configured:

```bash
# ✅ Docker and Docker Compose installed
docker --version
docker compose version

# ✅ Repository structure complete
ls -R ~/dev-network/beast/

# ✅ Configuration files present
test -f beast/docker/docker-compose.yml && echo "✓ docker-compose.yml exists"
test -f beast/docker/.env && echo "✓ .env exists"
test -f beast/monitoring/prometheus/prometheus.yml && echo "✓ Prometheus config exists"
test -f beast/monitoring/grafana/provisioning/datasources/prometheus.yml && echo "✓ Grafana datasource config exists"
test -f beast/cloudflare/config.yml && echo "✓ Cloudflare config exists"

# ✅ Docker network will be created: monitoring
# ✅ Docker volumes will be created: prometheus-data, grafana-data, portainer-data
```

---

## Docker Health Verification

### Docker Service Startup

```bash
cd ~/dev-network/beast/docker

# Start monitoring stack (all services)
docker compose up -d

# Expected output: Creating prometheus ... done, Creating node-exporter ... done, etc.

# Verify all containers are running
docker compose ps

# Expected: All 6 containers UP and running
# - prometheus (port 9090)
# - node-exporter (port 9100)
# - cadvisor (port 8080)
# - grafana (port 3000)
# - portainer (port 9443)
# - cloudflared (no exposed ports, tunnel mode)
```

### Container Health Checks

```bash
# Monitor health check status
docker compose ps --format "table {{.Name}}\t{{.Status}}"

# Check container logs for errors
docker logs prometheus | tail -20
docker logs node-exporter | tail -20
docker logs cadvisor | tail -20
docker logs grafana | tail -20
docker logs portainer | tail -20

# Expected: No ERROR or FATAL messages

# Check resource usage
docker stats --no-stream

# Expected: All containers consuming reasonable resources (<500MB each)
```

---

## Prometheus Validation

### Metrics Collection

```bash
# ✅ Prometheus is responsive
curl -s http://localhost:9090/-/healthy
# Expected: response 200 OK

# ✅ Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets'

# Expected output: 3 targets UP
# [
#   {"job": "prometheus", "state": "up", ...},
#   {"job": "node-exporter", "state": "up", ...},
#   {"job": "cadvisor", "state": "up", ...}
# ]

# ✅ Query available metrics
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq '.data.result'

# Expected: All 3 services return value 1 (up)
```

### Metric Collection Test

```bash
# ✅ System metrics from Node Exporter
curl -s 'http://localhost:9090/api/v1/query?query=node_memory_MemAvailable_bytes' \
  | jq '.data.result[0].value'
# Expected: Beast system RAM available in bytes

# ✅ Container metrics from cAdvisor
curl -s 'http://localhost:9090/api/v1/query?query=container_memory_usage_bytes' \
  | jq '.data.result | length'
# Expected: Number of running containers (should be > 0)

# ✅ 30-day retention configured
curl -s 'http://localhost:9090/status' | jq '.tsdb.retention'
# Expected: 30d or 720h
```

---

## Grafana Validation

### Web Interface Access

```bash
# ✅ Grafana is responsive
curl -s http://localhost:3000/api/health | jq '.database'
# Expected: "ok"

# ✅ Grafana login page accessible
curl -I http://localhost:3000
# Expected: HTTP 200 OK

# ✅ Login with admin credentials
# Username: admin
# Password: (from .env GF_SECURITY_ADMIN_PASSWORD)
# Web UI: http://192.168.68.100:3000
```

### Prometheus Datasource

```bash
# ✅ Check provisioned datasources
curl -s http://localhost:3000/api/datasources | jq '.[] | {name, type, url}'

# Expected output:
# {
#   "name": "Prometheus",
#   "type": "prometheus",
#   "url": "http://prometheus:9090"
# }

# ✅ Verify datasource is working
curl -s 'http://localhost:3000/api/datasources/uid/prometheus/health'
# Expected: {"status": "ok"}
```

### Dashboard Auto-Load

```bash
# ✅ Check provisioned dashboards
curl -s http://localhost:3000/api/search | jq '.[] | {title, type}'

# Expected output includes:
# {
#   "title": "Node Exporter Full",
#   "type": "dash-db"
# }
# {
#   "title": "Docker Containers",
#   "type": "dash-db"
# }
```

### Dashboard Data Verification

**Via Web UI (http://192.168.68.100:3000):**

1. Login with admin credentials
2. Navigate to Dashboards
3. Open "Node Exporter Full" dashboard
   - ✅ Panels show system metrics (CPU, RAM, Disk)
   - ✅ No "No Data" errors
   - ✅ Graphs update in real-time

4. Open "Docker Containers" dashboard
   - ✅ Shows container CPU/memory usage
   - ✅ Lists all running containers
   - ✅ Data refreshes automatically

---

## Portainer Validation

### Web Interface Access

```bash
# ✅ Portainer is responsive (ignore SSL warnings)
curl -k -I https://localhost:9443
# Expected: HTTP 200 OK

# ✅ Initial setup page accessible
# Web UI: https://192.168.68.100:9443
```

### Container Management

**Via Web UI (https://192.168.68.100:9443):**

1. Complete initial admin setup (first run only)
2. Connect to local Docker environment
3. ✅ All 6 containers visible:
   - prometheus
   - node-exporter
   - cadvisor
   - grafana
   - portainer
   - cloudflared

4. ✅ Container statistics displayed:
   - CPU usage
   - Memory usage
   - Network I/O

5. ✅ Test container operations:
   - Click "Grafana" → "Logs" (view logs)
   - Click "Grafana" → "Stats" (view metrics)
   - Click "Restart" (should restart cleanly)

---

## Cloudflare Tunnel Validation

### Prerequisites for Tunnel Testing

⚠️ **Requires**:
- Cloudflare account with tunnel created
- Domain configured with DNS routes
- Tunnel credentials stored at ~/.cloudflared/

```bash
# ✅ Tunnel configuration present
test -f ~/dev-network/beast/cloudflare/config.yml && echo "✓ Config exists"

# ✅ Cloudflare tunnel CLI installed (if doing manual setup)
cloudflared tunnel list
# Expected: Shows "beast-tunnel" with HEALTHY status
```

### Tunnel Status

```bash
# ✅ Cloudflared container running
docker ps | grep cloudflared
# Expected: Container UP and running

# ✅ Check tunnel logs
docker logs cloudflared | tail -20
# Expected: "Tunnel ready" or "Connected successfully"

# ✅ Check Cloudflare Dashboard
# https://dash.cloudflare.com/ → Access → Tunnels
# Expected: beast-tunnel status shows "HEALTHY"
```

### External HTTPS Access

**From external network (mobile hotspot / different WiFi):**

```bash
# ✅ Grafana accessible via HTTPS
curl -I https://grafana.yourdomain.com
# Expected: HTTP 302 (redirect to login) or 200 OK

# ✅ Portainer accessible via HTTPS
curl -k -I https://portainer.yourdomain.com
# Expected: HTTP 200 OK (or login page)

# ✅ No certificate warnings
# (Certificates signed by Cloudflare, should be valid)
```

---

## Auto-Start Verification

```bash
# ✅ Services configured for auto-restart
grep "restart:" beast/docker/docker-compose.yml
# Expected: "restart: unless-stopped" for all services

# ✅ Simulate reboot (optional):
docker compose down
docker compose up -d

# Verify all services came back up
docker compose ps
```

---

## Security Checks

```bash
# ✅ .env file NOT in git
git status | grep ".env"
# Expected: No output (file is ignored)

# ✅ Tunnel credentials NOT in git
git status | grep "cloudflare/.*\.json"
# Expected: No output (credentials ignored)

# ✅ .gitignore properly configured
grep -E "\.env|\.json" .gitignore
# Expected: Patterns present for both .env and .json

# ✅ Only HTTPS exposed externally
# - Cloudflare tunnel provides encryption
# - No direct port 9090/3000/9443/8080 exposure
```

---

## Success Criteria Checklist

- ✅ All 6 Docker containers running
- ✅ Prometheus collecting from 3 targets (prometheus, node-exporter, cadvisor)
- ✅ Grafana showing 2 dashboards with live data
- ✅ Portainer can view and manage containers
- ✅ Cloudflare tunnel connected and healthy
- ✅ External HTTPS access working for Grafana and Portainer
- ✅ Services auto-restart on reboot
- ✅ No secrets exposed in git repository
- ✅ All health checks passing

---

## Troubleshooting

### Service Failed to Start

```bash
# Check logs
docker logs <service-name>

# Common issues:
# 1. Port already in use: sudo lsof -i :<port>
# 2. Permissions: Check docker socket ownership
# 3. Config error: Validate YAML files
```

### Prometheus Not Scraping

```bash
# Check scrape targets
curl http://localhost:9090/api/v1/targets

# Check prometheus logs
docker logs prometheus | grep "scrape"

# Common issues:
# 1. Service names DNS resolution (use docker network names)
# 2. Health check failures
# 3. Firewall between containers
```

### Grafana Dashboards Show No Data

```bash
# Check datasource connection
curl http://localhost:3000/api/datasources/uid/prometheus/health

# Verify Prometheus has data
curl 'http://localhost:9090/api/v1/query?query=up'

# Common issues:
# 1. Provisioning not loaded (check provisioning directory mount)
# 2. Dashboard UIDs don't match (manually import if needed)
# 3. Query syntax errors in dashboard panels
```

### Cloudflared Connection Failed

```bash
# Check tunnel credentials
ls -la ~/.cloudflared/
# Expected: *.json file exists with proper permissions

# Check tunnel config syntax
cat ~/dev-network/beast/cloudflare/config.yml
# Expected: Valid YAML with no errors

# Check Cloudflare dashboard
# https://dash.cloudflare.com/ → Access → Tunnels
# Look for error messages or diagnostics
```

---

## Performance Baseline

After successful validation, typical metrics:

- **Prometheus**: ~100-200MB memory, <1% CPU
- **Node Exporter**: ~10-30MB memory, <1% CPU
- **cAdvisor**: ~200-400MB memory, 1-2% CPU
- **Grafana**: ~250-350MB memory, <1% CPU (idle)
- **Portainer**: ~100-200MB memory, <1% CPU (idle)
- **Total Stack**: ~700MB-1.2GB memory at rest

---

**Phase 6, Step 6.1 Complete** ✓

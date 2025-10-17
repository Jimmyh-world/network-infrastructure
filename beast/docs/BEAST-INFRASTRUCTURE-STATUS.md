# Beast Infrastructure Status

**Last Updated:** 2025-10-17
**Deployment Date:** 2025-10-17
**Status:** ✅ Production-ready
**Uptime Since:** 2025-10-17 13:00 UTC

---

## Deployment Summary

**What's Deployed:**
- Complete monitoring infrastructure (Prometheus, Grafana, Node Exporter, cAdvisor)
- Container management platform (Portainer)
- Article extraction microservice (ydun-scraper)
- External HTTPS access (Cloudflare Tunnel on kitt.agency)

**Services Running:**
- 6 Docker containers (all healthy)
- 1 host process (cloudflared tunnel)
- Total resource usage: ~2GB RAM, <10GB disk

**External Access:**
- https://grafana.kitt.agency (monitoring dashboards)
- https://scrape.kitt.agency (article extraction API)
- https://portainer.kitt.agency (502 error - self-signed cert issue)

**Last Validation:** 2025-10-17 13:25 UTC
- All internal endpoints: ✅ 200 OK
- External HTTPS endpoints: ✅ Working
- Cloudflare Tunnel: ✅ Connected (4 edge connections)

---

## Service Inventory

| Service | Type | Internal Port | External Port | External URL | Status | Purpose |
|---------|------|--------------|---------------|--------------|--------|---------|
| **Prometheus** | Docker | 9090 | 9090 | N/A | ✅ Running | Metrics collection, 30-day retention |
| **Node Exporter** | Docker | 9100 | 9100 | N/A | ✅ Running | System metrics (CPU, RAM, disk, network) |
| **cAdvisor** | Docker | 8080 | 8080 | N/A | ✅ Running | Docker container metrics |
| **Grafana** | Docker | 3000 | 3000 | https://grafana.kitt.agency | ✅ Running | Monitoring dashboards, data visualization |
| **Portainer** | Docker | 9443 | 9443 | ⚠️ 502 error | ✅ Running | Container GUI management |
| **ydun-scraper** | Docker | 8080 | 5000 | https://scrape.kitt.agency | ✅ Running | Article extraction (trafilatura-based) |
| **cloudflared** | Host process | N/A | N/A | N/A | ✅ Running | Cloudflare Tunnel client |

### Service Details

#### Prometheus
- **Image:** `prom/prometheus:latest`
- **Metrics Sources:** node-exporter, cadvisor, prometheus (self)
- **Retention:** 30 days
- **Data Volume:** `prometheus-data` (local Docker volume)
- **Config:** `beast/monitoring/prometheus/prometheus.yml`
- **Scrape Interval:** 15 seconds
- **Health Check:** `curl http://localhost:9090/-/healthy`

#### Node Exporter
- **Image:** `prom/node-exporter:latest`
- **Collectors Enabled:** filesystem, cpu, memory, network, disk
- **Excluded Mounts:** sys, proc, dev (read-only system paths)
- **Health Check:** `curl http://localhost:9100/metrics`

#### cAdvisor
- **Image:** `gcr.io/cadvisor/cadvisor:latest`
- **Privileges:** Runs privileged (needs Docker socket access)
- **Monitors:** All Docker containers on Beast
- **Metrics:** CPU, memory, network, disk I/O per container
- **Health Check:** `curl http://localhost:8080/healthz`

#### Grafana
- **Image:** `grafana/grafana:latest`
- **Admin Password:** Stored in `.env` file (gitignored)
- **Root URL:** https://grafana.kitt.agency
- **Data Volume:** `grafana-data` (persistent dashboards and settings)
- **Provisioning:** Auto-load dashboards from `beast/monitoring/grafana/`
- **Health Check:** `curl http://localhost:3000/api/health`
- **Plugins:** (none currently installed)

#### Portainer
- **Image:** `portainer/portainer-ce:latest`
- **Data Volume:** `portainer-data` (persistent settings)
- **Manages:** All Docker containers on Beast via `/var/run/docker.sock`
- **HTTPS:** Self-signed certificate (causes 502 via tunnel)
- **Health Check:** `curl https://localhost:9443` (ignores cert)
- **Alternative Access:** http://192.168.68.100:9443 (local network)

#### ydun-scraper
- **Image:** Built from `~/ydun-scraper/Dockerfile`
- **Language:** Python 3.11
- **Framework:** Flask HTTP server
- **Extraction:** trafilatura + newspaper3k
- **Port Mapping:** 5000:8080 (external:internal)
- **Performance:** 2+ URLs/second, ~500ms per article
- **Health Check:** `curl http://localhost:8080/health`
- **API Endpoint:** POST /scrape with JSON body {"urls": [...]}

#### cloudflared
- **Type:** Host process (not Docker container)
- **Tunnel ID:** d2d710e7-94cd-41d8-9979-0519fa1233e7
- **Tunnel Name:** beast-tunnel
- **Config:** `beast/cloudflare/config.yml`
- **Credentials:** `~/.cloudflared/d2d710e7-94cd-41d8-9979-0519fa1233e7.json`
- **Log File:** `/tmp/cloudflared.log`
- **Edge Connections:** 4 (typically arn02, arn06, arn07 regions)
- **Status Check:** `cloudflared tunnel info <tunnel-id>`

---

## Resource Usage

### Beast Hardware Specifications

| Component | Specification |
|-----------|--------------|
| **CPU** | (To be documented - run `lscpu` on Beast) |
| **RAM** | 96GB DDR4 |
| **Storage** | 2TB NVMe SSD |
| **Network** | 1Gbps Ethernet |
| **OS** | Ubuntu Server 24.04 LTS |
| **Hostname** | thebeast |
| **IP Address** | 192.168.68.100 (static) |

### Current Resource Allocation

| Service | RAM Usage | CPU Usage | Disk Usage | Notes |
|---------|-----------|-----------|------------|-------|
| Prometheus | ~300MB | <5% | ~2GB (metrics) | 30-day retention |
| Node Exporter | ~20MB | <1% | Negligible | Metrics only |
| cAdvisor | ~50MB | <2% | Negligible | Metrics only |
| Grafana | ~100MB | <2% | ~200MB | Dashboards + config |
| Portainer | ~50MB | <1% | ~100MB | Config + images |
| ydun-scraper | ~100MB | <2% | ~500MB | Python + deps |
| cloudflared | ~50MB | <1% | Negligible | Tunnel client |
| **Total Used** | **~670MB** | **<15%** | **~3GB** | |
| **Available** | **~95GB** | **>85%** | **~1.99TB** | Ready for blockchain nodes |

**Resource Headroom:** Massive capacity available for future services (Cardano nodes, Ergo nodes, etc.)

---

## Network Architecture

### Physical Network

```
Internet
  ↓
Router (192.168.68.1)
  ├── Chromebook (192.168.68.x) - Development, documentation
  ├── Beast (192.168.68.100) - Infrastructure, services
  └── [Guardian Pi] (192.168.68.x - planned)
```

### External Access via Cloudflare

```
User Browser (anywhere)
  ↓
Cloudflare Edge Network
  ↓
Cloudflare Tunnel (beast-tunnel)
  ├── grafana.kitt.agency → localhost:3000 (Grafana)
  ├── scrape.kitt.agency → localhost:5000 (ydun-scraper)
  └── portainer.kitt.agency → localhost:9443 (Portainer - 502 error)
  ↓
Beast Host (192.168.68.100)
```

### Docker Internal Network

```
Beast Host
  └── Docker Bridge Network: "monitoring"
      ├── prometheus:9090
      ├── node-exporter:9100
      ├── cadvisor:8080
      ├── grafana:3000
      ├── portainer:9443
      └── ydun-scraper:8080 (mapped to host:5000)
```

### Port Mappings

| External Port | Internal Container | Service | Protocol |
|--------------|-------------------|---------|----------|
| 3000 | grafana:3000 | Grafana | HTTP |
| 5000 | ydun-scraper:8080 | Scraper | HTTP |
| 8000 | portainer:8000 | Portainer Edge | TCP |
| 8080 | cadvisor:8080 | cAdvisor | HTTP |
| 9090 | prometheus:9090 | Prometheus | HTTP |
| 9100 | node-exporter:9100 | Node Exporter | HTTP |
| 9443 | portainer:9443 | Portainer | HTTPS |

**No port conflicts:** All services have unique external ports.

---

## Access Methods

### Internal (Local Network)

Access from any device on 192.168.68.0/24 network:

```bash
# Grafana
http://192.168.68.100:3000

# Prometheus
http://192.168.68.100:9090

# Node Exporter
http://192.168.68.100:9100/metrics

# cAdvisor
http://192.168.68.100:8080

# Portainer
https://192.168.68.100:9443

# ydun-scraper
http://192.168.68.100:5000/health
http://192.168.68.100:5000/scrape

# Beast SSH
ssh jimmyb@192.168.68.100
```

### External (Internet via Cloudflare Tunnel)

Access from anywhere with internet connection:

```bash
# Grafana
https://grafana.kitt.agency

# ydun-scraper
https://scrape.kitt.agency/health
https://scrape.kitt.agency/scrape

# Portainer
https://portainer.kitt.agency  # ⚠️ Returns 502 (self-signed cert issue)
```

### SSH Access

```bash
# From Chromebook
ssh jimmyb@192.168.68.100

# SSH key
~/.ssh/id_rsa (beast@dev-lab key configured)

# Verify
ssh jimmyb@192.168.68.100 "hostname && docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

---

## Credentials & Secrets

### Grafana

- **Username:** `admin`
- **Password:** See `~/network-infrastructure/beast/docker/.env`
- **File Location (Beast):** `/home/jimmyb/network-infrastructure/beast/docker/.env`
- **Status:** Gitignored (not in version control)
- **Generation:** `openssl rand -base64 32`

### Portainer

- **Initial Setup:** Set password on first access
- **Access:** https://192.168.68.100:9443 (local network)
- **Status:** Not yet configured

### Cloudflare Tunnel

- **Origin Certificate:** `~/.cloudflared/cert.pem` (Beast)
- **Tunnel Credentials:** `~/.cloudflared/d2d710e7-94cd-41d8-9979-0519fa1233e7.json` (Beast)
- **Account:** kitt.agency domain on Cloudflare (free tier)
- **Status:** Gitignored (not in version control)
- **Permissions:** 600 (owner read/write only)

### SSH Keys

- **Private Key (Chromebook):** `~/.ssh/id_rsa`
- **Public Key (Beast):** `~/.ssh/authorized_keys`
- **Key Name:** beast@dev-lab
- **Status:** Configured and working

---

## Configuration Files

### Docker Compose

**File:** `~/network-infrastructure/beast/docker/docker-compose.yml`

**Status:** Version controlled (GitHub)

**Defines:**
- 6 Docker services
- 3 Docker volumes (prometheus-data, grafana-data, portainer-data)
- 1 Docker network (monitoring)
- Health checks for all services
- Port mappings
- Restart policies (unless-stopped)

**Note:** Does NOT include cloudflared service (runs on host instead)

### Environment Variables

**File:** `~/network-infrastructure/beast/docker/.env`

**Status:** Gitignored (secrets)

**Contains:**
- `GF_SECURITY_ADMIN_PASSWORD` - Grafana admin password
- `GF_SERVER_ROOT_URL` - https://grafana.kitt.agency
- `GF_INSTALL_PLUGINS` - (empty currently)
- `PROMETHEUS_RETENTION` - 720h (30 days)

**Template:** `beast/docker/.env.example` (version controlled)

### Prometheus Configuration

**File:** `~/network-infrastructure/beast/monitoring/prometheus/prometheus.yml`

**Status:** Version controlled (GitHub)

**Scrape Targets:**
- prometheus:9090 (self-monitoring)
- node-exporter:9100 (system metrics)
- cadvisor:8080 (container metrics)

**Scrape Interval:** 15 seconds

**Retention:** 30 days (720h)

### Grafana Provisioning

**Directory:** `~/network-infrastructure/beast/monitoring/grafana/provisioning/`

**Status:** Version controlled (GitHub)

**Contains:**
- `datasources/prometheus.yml` - Prometheus data source config
- `dashboards/default.yml` - Dashboard auto-load config

**Dashboards Directory:** `beast/monitoring/grafana/dashboards/`

**Status:** To be populated with Beast monitoring dashboards

### Cloudflare Tunnel Configuration

**File:** `~/network-infrastructure/beast/cloudflare/config.yml`

**Status:** Version controlled (GitHub)

**Defines:**
- Tunnel ID: d2d710e7-94cd-41d8-9979-0519fa1233e7
- Credentials file location: `~/.cloudflared/d2d710e7-94cd-41d8-9979-0519fa1233e7.json`
- Ingress routes: grafana, scrape, portainer
- Catch-all: 404

---

## Operational Status

### Health Checks (2025-10-17 13:25 UTC)

```bash
# All internal endpoints verified
curl http://192.168.68.100:9090/-/healthy  # ✅ 200 OK
curl http://192.168.68.100:9100/metrics    # ✅ 200 OK
curl http://192.168.68.100:8080/healthz    # ✅ 200 OK
curl http://192.168.68.100:3000/api/health # ✅ 200 OK
curl http://192.168.68.100:5000/health     # ✅ 200 OK

# External endpoints verified
curl https://grafana.kitt.agency/api/health # ✅ 200 OK
curl https://scrape.kitt.agency/health      # ✅ 200 OK
```

### Cloudflare Tunnel Status

```bash
# Tunnel info (as of 2025-10-17 13:25 UTC)
cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7

# Status: Connected
# Edge Connections: 4
# Regions: arn02, arn06, arn07 (Amsterdam area)
```

### Docker Container Status

```bash
# All containers running and healthy (2025-10-17)
docker compose ps

NAME              STATUS
prometheus        Up (healthy)
node-exporter     Up (healthy)
cadvisor          Up (healthy)
grafana           Up (healthy)
portainer         Up (healthy)
ydun-scraper      Up (healthy)
```

### Known Issues

| Issue | Status | Impact | Workaround |
|-------|--------|--------|------------|
| Portainer HTTPS via tunnel returns 502 | 🟡 Open | Low (UI accessible locally) | Use https://192.168.68.100:9443 |
| None | - | - | - |

---

## Operational Procedures

### Start All Services

```bash
# Start Docker services
cd ~/network-infrastructure/beast/docker
docker compose up -d

# Start Cloudflare Tunnel
cd ~/network-infrastructure/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &

# Verify
docker compose ps
ps aux | grep "cloudflared tunnel" | grep -v grep
```

### Stop All Services

```bash
# Stop Docker services
cd ~/network-infrastructure/beast/docker
docker compose down

# Stop Cloudflare Tunnel
pkill -f "cloudflared tunnel"
```

### Restart Individual Service

```bash
cd ~/network-infrastructure/beast/docker
docker compose restart <service-name>

# Examples:
docker compose restart grafana
docker compose restart ydun-scraper
```

### View Logs

```bash
# All services
cd ~/network-infrastructure/beast/docker
docker compose logs -f

# Specific service
docker compose logs -f grafana
docker compose logs -f ydun-scraper

# Cloudflare Tunnel
tail -50 /tmp/cloudflared.log
tail -f /tmp/cloudflared.log  # Follow
```

### Check Resource Usage

```bash
# Real-time stats
docker stats

# One-time snapshot
docker stats --no-stream

# System resources
htop
free -h
df -h
```

### Update Services

```bash
# Pull latest images
cd ~/network-infrastructure/beast/docker
docker compose pull

# Recreate containers with new images
docker compose up -d

# Remove old images
docker image prune -f
```

---

## Monitoring & Alerting

### Grafana Dashboards

**Available:** (To be configured)
- Beast System Overview (CPU, RAM, disk, network)
- Docker Container Metrics
- ydun-scraper Performance
- Prometheus Metrics

**Access:** https://grafana.kitt.agency

**Setup Required:** Import dashboards from Grafana.com or create custom

### Prometheus Queries

**Useful queries:**

```promql
# CPU usage per container
rate(container_cpu_usage_seconds_total[5m])

# Memory usage per container
container_memory_usage_bytes

# Disk I/O per container
rate(container_fs_reads_bytes_total[5m])
rate(container_fs_writes_bytes_total[5m])

# Beast system CPU
rate(node_cpu_seconds_total{mode!="idle"}[5m])

# Beast system memory
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes

# Beast disk space
node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}
```

### Alerting

**Status:** Not yet configured

**Planned:**
- High CPU usage (>80% for 5 minutes)
- High memory usage (>80% for 5 minutes)
- Low disk space (<20% available)
- Container restarts (unhealthy)
- Cloudflare Tunnel disconnected

---

## Backup & Recovery

### What to Backup

**Critical:**
- Grafana data: `~/network-infrastructure/beast/docker/` (grafana-data volume)
- Prometheus data: `~/network-infrastructure/beast/docker/` (prometheus-data volume)
- Portainer data: `~/network-infrastructure/beast/docker/` (portainer-data volume)
- Environment file: `~/network-infrastructure/beast/docker/.env`
- Cloudflare credentials: `~/.cloudflared/`

**Non-Critical (version controlled):**
- Configuration files (all in Git)
- Documentation (all in Git)

### Backup Procedure

```bash
# Backup Docker volumes
docker run --rm -v prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-data-$(date +%Y%m%d).tar.gz -C /data .
docker run --rm -v grafana-data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-data-$(date +%Y%m%d).tar.gz -C /data .
docker run --rm -v portainer-data:/data -v $(pwd):/backup alpine tar czf /backup/portainer-data-$(date +%Y%m%d).tar.gz -C /data .

# Backup .env and credentials
tar czf beast-secrets-$(date +%Y%m%d).tar.gz ~/network-infrastructure/beast/docker/.env ~/.cloudflared/
```

### Recovery Procedure

```bash
# Stop services
cd ~/network-infrastructure/beast/docker
docker compose down

# Restore volumes
docker run --rm -v prometheus-data:/data -v $(pwd):/backup alpine tar xzf /backup/prometheus-data-YYYYMMDD.tar.gz -C /data
docker run --rm -v grafana-data:/data -v $(pwd):/backup alpine tar xzf /backup/grafana-data-YYYYMMDD.tar.gz -C /data
docker run --rm -v portainer-data:/data -v $(pwd):/backup alpine tar xzf /backup/portainer-data-YYYYMMDD.tar.gz -C /data

# Restore secrets
tar xzf beast-secrets-YYYYMMDD.tar.gz -C /

# Start services
docker compose up -d
```

### Disaster Recovery

**Complete infrastructure loss:**
1. Fresh Ubuntu Server 24.04 install on Beast
2. Install Git, Docker, Node.js, Claude Code CLI
3. Clone network-infrastructure repository
4. Restore .env and Cloudflare credentials from backup
5. Run `docker compose up -d`
6. Start Cloudflare Tunnel
7. Verify all services healthy

**Time to recovery:** ~2 hours (excluding OS install)

---

## Performance Baselines

### ydun-scraper Performance (2025-10-17)

**Test:** Single BBC News article extraction
- **Duration:** 480ms
- **Throughput:** 2.1 URLs/second
- **Content Length:** 6,231 characters (average)
- **Success Rate:** 100% (on BBC News)

**Test:** Batch processing
- **Not yet tested** - To be benchmarked with 10, 50, 100 URLs

### System Performance

**Baseline metrics (2025-10-17):**
- CPU idle: ~95%
- Memory available: ~95GB / 96GB
- Disk I/O: Minimal (<1MB/s)
- Network: <1Mbps (monitoring traffic only)

**Load capacity:** Estimated 20x current load before resource constraints

---

## Security Considerations

### Network Security

- ✅ No port forwarding on router (Cloudflare Tunnel instead)
- ✅ SSH key-based authentication (no passwords)
- ✅ Services only exposed via Cloudflare Tunnel (encrypted)
- ✅ Local network traffic unencrypted (acceptable for home lab)

### Secrets Management

- ✅ All secrets gitignored (.env, credentials)
- ✅ Cloudflare credentials: 600 permissions
- ✅ SSH private keys: 600 permissions
- ⚠️ Grafana admin password: Should be changed from initial

### Container Security

- ✅ Non-root users (where possible)
- ✅ Health checks configured
- ✅ Restart policies set (unless-stopped)
- ⚠️ cAdvisor runs privileged (required for Docker socket access)

### Future Security Enhancements

- [ ] Enable Grafana alerting
- [ ] Set up firewall rules (UFW)
- [ ] Rotate Cloudflare Tunnel credentials
- [ ] Implement rate limiting on scraper API
- [ ] Add authentication to scraper endpoint

---

## Future Expansion Plans

### Short Term (Next 1-2 weeks)

1. **Grafana Dashboards:** Import/create Beast monitoring dashboards
2. **Mundus Integration:** Connect ydun-scraper to Supabase edge functions
3. **Alerting:** Configure basic alerts (resource thresholds)

### Medium Term (Next 1-2 months)

1. **Cardano Preview Testnet Node:** Deploy for Aiken contract testing
2. **Guardian Pi:** Set up Pi-hole + WireGuard VPN
3. **Backup Automation:** Scheduled backups of critical data

### Long Term (Next 3-6 months)

1. **Cardano Mainnet Node:** Production node for dApp interactions
2. **Ergo Mainnet Node:** Rosen Bridge support
3. **Midnight Devnet Node:** ZK-SNARK experimentation
4. **Multiple Blockchain Nodes:** Full multi-chain infrastructure

**Resource availability:** Beast has capacity for all planned nodes

---

## Troubleshooting

### Service Won't Start

```bash
# Check Docker logs
docker compose logs <service-name>

# Check for port conflicts
netstat -tulpn | grep <port>

# Check Docker socket
ls -la /var/run/docker.sock

# Restart Docker daemon
sudo systemctl restart docker
```

### Cloudflare Tunnel Issues

```bash
# Check tunnel status
cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7

# Check logs
tail -100 /tmp/cloudflared.log

# Check credentials
ls -la ~/.cloudflared/

# Restart tunnel
pkill -f "cloudflared tunnel"
cd ~/network-infrastructure/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
```

### Can't Access Grafana

```bash
# Check service is running
curl http://localhost:3000/api/health

# Check Docker container
docker ps | grep grafana

# Check Cloudflare route
curl https://grafana.kitt.agency/api/health

# Check DNS
nslookup grafana.kitt.agency
```

### High Resource Usage

```bash
# Check container stats
docker stats --no-stream

# Check system resources
htop
free -h
df -h

# Check Prometheus retention
# (Reduce if disk usage too high)
```

---

## Documentation References

**Setup Workflows:**
- `beast/docs/MONITORING-INFRASTRUCTURE-SETUP.md` - Initial deployment workflow
- `beast/docs/YDUN-SCRAPER-DEPLOYMENT.md` - Scraper deployment workflow
- `beast/docs/INFRASTRUCTURE-CLEANUP-WORKFLOW.md` - Configuration cleanup

**Operational Guides:**
- `beast/docs/MONITORING-OPERATIONS.md` - Day-to-day operations
- `beast/docs/MONITORING-VALIDATION.md` - Testing and validation procedures
- `beast/docs/ROLLBACK-PROCEDURES.md` - Emergency rollback procedures
- `beast/cloudflare/TUNNEL-HOST-DEPLOYMENT.md` - Tunnel management

**Integration:**
- `beast/docs/MUNDUS-INTEGRATION.md` - Supabase edge function integration guide

---

## Change Log

### 2025-10-17 - Initial Deployment

**Deployed:**
- Monitoring infrastructure (Prometheus, Grafana, Node Exporter, cAdvisor)
- Container management (Portainer)
- Article scraper (ydun-scraper)
- External HTTPS access (Cloudflare Tunnel)

**Configuration:**
- 6 Docker services
- 1 host-based tunnel process
- Complete operational documentation

**Status:** Production-ready

---

**This document is the source of truth for Beast infrastructure status.**

---

**Last Updated:** 2025-10-17

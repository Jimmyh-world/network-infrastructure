# Guardian Tier 1 Deployment Specification

**Created:** 2025-10-21
**Target:** Guardian Pi 5 (192.168.68.10 / gaurdian via Tailscale)
**Goal:** Deploy complete network security monitoring stack
**Duration:** Estimated 2-3 hours

---

## Deployment Overview

### Components to Deploy

1. **Docker** - Container platform for monitoring stack
2. **Prometheus** - Metrics collection (port 9090)
3. **Grafana** - Dashboards (port 3000)
4. **ntopng** - Network traffic analysis (port 3001)
5. **Suricata** - IDS/IPS (threat detection)
6. **Alert System** - Security event notifications

---

## Prerequisites ✅ COMPLETE

- [x] Guardian Pi 5 operational at 192.168.68.10
- [x] Pi-hole running on Guardian
- [x] Tailscale SSH access working
- [x] 49GB disk space available
- [x] 7.5GB RAM available
- [x] User: jamesb

---

## Phase 1: Docker Installation

### 🔴 RED (IMPLEMENT)

```bash
# SSH to Guardian
ssh guardian

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add jamesb to docker group
sudo usermod -aG docker jamesb

# Install Docker Compose
sudo apt install -y docker-compose

# Reboot to apply group membership
sudo reboot
```

### 🟢 GREEN (VALIDATE)

```bash
# After reboot, SSH back in
ssh guardian

# Verify Docker
docker --version
docker-compose --version
docker ps

# Check Docker service
sudo systemctl status docker
```

**Success Criteria:**
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Docker service running
- [ ] Can run docker commands without sudo

---

## Phase 2: Monitoring Stack Deployment

### 🔴 RED (IMPLEMENT)

```bash
# Create monitoring directory
mkdir -p ~/guardian-monitoring
cd ~/guardian-monitoring

# Create docker-compose.yml
# (See configuration below)

# Create Prometheus config
mkdir -p prometheus
# (See prometheus.yml below)

# Start stack
docker-compose up -d
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  # Prometheus - Metrics Collection
  prometheus:
    image: prom/prometheus:latest
    container_name: guardian-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
    restart: unless-stopped
    networks:
      - monitoring

  # Grafana - Dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: guardian-grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-changeme}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    restart: unless-stopped
    networks:
      - monitoring

  # ntopng - Network Monitoring
  ntopng:
    image: vimagick/ntopng:latest
    container_name: guardian-ntopng
    ports:
      - "3001:3000"
    network_mode: host
    cap_add:
      - NET_ADMIN
      - NET_RAW
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:

networks:
  monitoring:
    driver: bridge
```

### Prometheus Configuration

**File:** `prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Guardian Pi metrics (if node-exporter added later)
  - job_name: 'guardian'
    static_configs:
      - targets: ['localhost:9100']
```

### 🟢 GREEN (VALIDATE)

```bash
# Check containers
docker-compose ps
# Should show 3 containers running

# Test Prometheus
curl http://localhost:9090/-/healthy
# Should return: Prometheus Server is Healthy.

# Test Grafana
curl http://localhost:3000/api/health
# Should return JSON with status

# Test ntopng (may need a few seconds to start)
curl -I http://localhost:3001
# Should return HTTP 200

# Check logs
docker-compose logs --tail 50
```

**Success Criteria:**
- [ ] All 3 containers running
- [ ] Prometheus healthy
- [ ] Grafana accessible
- [ ] ntopng responding
- [ ] No error logs

---

## Phase 3: Suricata IDS Deployment

### 🔴 RED (IMPLEMENT)

```bash
# Install Suricata
sudo apt update
sudo apt install -y suricata

# Configure Suricata for home network
sudo nano /etc/suricata/suricata.yaml
# Update HOME_NET to: "192.168.68.0/24"

# Update Suricata rules
sudo suricata-update

# Enable and start Suricata
sudo systemctl enable suricata
sudo systemctl start suricata
```

### 🟢 GREEN (VALIDATE)

```bash
# Check Suricata status
sudo systemctl status suricata

# Check Suricata logs
sudo tail -50 /var/log/suricata/suricata.log

# Test detection (from another machine)
# curl http://testmynids.org/uid/index.html
# Suricata should log this test alert

# Check alerts
sudo tail -20 /var/log/suricata/fast.log
```

**Success Criteria:**
- [ ] Suricata service running
- [ ] Rules updated
- [ ] Logs being generated
- [ ] Test alert detected

---

## Phase 4: Access Configuration

### Services Accessibility

**From local network (192.168.68.x):**
```
Grafana:    http://192.168.68.10:3000
Prometheus: http://192.168.68.10:9090
ntopng:     http://192.168.68.10:3001
Pi-hole:    http://192.168.68.10/admin (or http://192.168.68.53/admin)
```

**Via Tailscale (from anywhere):**
```
Grafana:    http://gaurdian:3000
Prometheus: http://gaurdian:9090
ntopng:     http://gaurdian:3001
Pi-hole:    http://gaurdian/admin
```

**Via SSH tunnels:**
```bash
# Grafana
ssh -L 3000:localhost:3000 guardian

# Prometheus
ssh -L 9090:localhost:9090 guardian

# ntopng
ssh -L 3001:localhost:3001 guardian
```

---

## Phase 5: Alert System (Basic)

### 🔴 RED (IMPLEMENT)

For now, alerts will be log-based. Advanced alerting (email/Slack) can be added later.

**Monitor logs:**
```bash
# Watch Suricata alerts in real-time
sudo tail -f /var/log/suricata/fast.log

# Check Pi-hole query log
pihole -t
```

**Future:** Integrate with Grafana Alerts, Prometheus Alertmanager

---

## 🔵 CHECKPOINT (GATE)

### Validation Checklist

**Docker:**
- [ ] Docker installed and running
- [ ] Docker Compose operational
- [ ] User in docker group

**Monitoring Stack:**
- [ ] Prometheus collecting metrics
- [ ] Grafana accessible (http://192.168.68.10:3000)
- [ ] ntopng monitoring traffic (http://192.168.68.10:3001)
- [ ] All containers auto-restart enabled

**Security:**
- [ ] Suricata IDS running
- [ ] Suricata rules updated
- [ ] Test alert detected
- [ ] Pi-hole still operational

**Network:**
- [ ] All services accessible on local network
- [ ] All services accessible via Tailscale
- [ ] No port conflicts
- [ ] Firewall allows connections

**Resources:**
- [ ] RAM usage acceptable (<2GB for all services)
- [ ] Disk space adequate (>40GB free)
- [ ] CPU usage reasonable (<50%)

---

## Rollback Procedures

### Stop Monitoring Stack
```bash
cd ~/guardian-monitoring
docker-compose down
```

### Remove Docker
```bash
sudo systemctl stop docker
sudo apt remove --purge docker-ce docker-ce-cli containerd.io
sudo rm -rf /var/lib/docker
```

### Stop Suricata
```bash
sudo systemctl stop suricata
sudo systemctl disable suricata
```

---

## Performance Expectations

**Expected Resource Usage:**

```
RAM Usage:
├─ Pi-hole: ~100MB
├─ Prometheus: ~200MB
├─ Grafana: ~150MB
├─ ntopng: ~200MB
├─ Suricata: ~300MB
├─ System: ~400MB
└─ Total: ~1.35GB / 8GB (83% free)

CPU Usage:
├─ Idle: ~15-20%
├─ Active monitoring: ~25-35%
└─ Spike during attacks: up to 60%

Disk Usage:
├─ Docker images: ~1GB
├─ Prometheus data (30 days): ~500MB
├─ Suricata logs: ~100MB/week
└─ Total: ~2GB + growth
```

---

## Security Considerations

**Exposed Services:**
- All Guardian services should be internal-only (no Cloudflare Tunnel)
- Access via Tailscale VPN or local network
- No direct internet exposure
- Consider adding authentication to ntopng (future)

**Credentials:**
- Grafana admin password: Set via environment variable
- ntopng: No auth by default (local network only)
- Pi-hole: Already has web password

---

## Next Steps After Tier 1

1. **Immediate:**
   - Monitor Suricata alerts for 24-48 hours
   - Check ntopng to identify all network devices
   - Create basic Grafana dashboard for Guardian

2. **Short-term (1-2 weeks):**
   - Fine-tune Suricata rules (reduce false positives)
   - Set up Grafana alerting
   - Configure network-wide DNS (Deco → 192.168.68.10)

3. **Long-term (Guardian Tier 2):**
   - Deploy always-on intelligence platform
   - RAG knowledge base monitoring
   - Wake-on-LAN orchestration
   - Advanced alerting (email, Slack, Telegram)

---

## Documentation Updates Needed

After successful deployment:
- [ ] Update `/home/jimmyb/dev-network/docs/ACCESS-METHODS.md`
- [ ] Update `/home/jimmyb/dev-network/docs/NEXT-SESSION-START-HERE.md`
- [ ] Update `/home/jimmyb/dev-guardian/STATUS.md`
- [ ] Create `/home/jimmyb/dev-network/guardian/docs/TIER1-DEPLOYMENT-SUCCESS.md`

---

**This spec follows Jimmy's Workflow: RED (Implement) → GREEN (Validate) → CHECKPOINT (Gate)**

**Estimated Total Time:** 2-3 hours
**Status:** Ready for execution

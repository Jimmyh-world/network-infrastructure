# Beast Monitoring Infrastructure - Operations Guide

**Document**: Operational Procedures
**Date Created**: 2025-10-17
**Version**: 1.0

---

## Quick Start

```bash
# Navigate to docker directory
cd ~/network-infrastructure/beast/docker

# Start all monitoring services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Stop with volume cleanup (full reset)
docker compose down -v
```

---

## Service Access

### Internal (LAN - 192.168.68.x)

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| Prometheus | http://192.168.68.100:9090 | None | Metrics queries, targets page |
| Grafana | http://192.168.68.100:3000 | admin / (from .env) | Dashboards, data visualization |
| Portainer | https://192.168.68.100:9443 | admin account | Container management |
| Node Exporter | http://192.168.68.100:9100/metrics | None (raw metrics) | System metrics scraping |
| cAdvisor | http://192.168.68.100:8080 | None | Container metrics data |

### External (via Cloudflare Tunnel - HTTPS)

| Service | Domain | Credentials | Access |
|---------|--------|-------------|--------|
| Grafana | https://grafana.yourdomain.com | admin / (from .env) | Dashboards, monitoring |
| Portainer | https://portainer.yourdomain.com | admin account | Container management |

---

## Common Operations

### Starting the Stack

```bash
cd ~/network-infrastructure/beast/docker

# Start all services
docker compose up -d

# Wait for containers to be healthy (~30 seconds)
sleep 30

# Verify all running
docker compose ps --format "table {{.Names}}\t{{.Status}}"
```

### Stopping the Stack

```bash
cd ~/network-infrastructure/beast/docker

# Graceful stop (containers restarted on next up)
docker compose stop

# Complete shutdown (removes containers)
docker compose down

# Full reset with volume wipe
docker compose down -v
```

### Viewing Logs

```bash
# All services, last 50 lines
docker compose logs --tail=50

# Specific service
docker compose logs grafana

# Follow log output (real-time)
docker compose logs -f prometheus

# Filter logs by level or pattern
docker compose logs | grep ERROR
```

### Restarting Services

```bash
# Restart single service
docker compose restart grafana

# Restart all services
docker compose restart

# Hard restart (stop + start)
docker compose down && docker compose up -d
```

### Checking Service Health

```bash
# View all container health status
docker compose ps

# Detailed health check
docker inspect --format='{{json .State.Health}}' grafana | jq

# Manual health test
curl -s http://localhost:9090/-/healthy
curl -s http://localhost:3000/api/health | jq '.database'
curl -s http://localhost:9100/metrics | head
```

---

## Container Management

### Access Container Shell

```bash
# Connect to container shell
docker exec -it prometheus /bin/sh

# Or via Portainer web UI:
# Containers → [service-name] → Console
```

### View Container Resources

```bash
# Real-time stats all containers
docker stats

# One-time snapshot
docker stats --no-stream

# Specific container
docker stats prometheus
```

### Clean Up Docker Resources

```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Complete cleanup (remove dangling resources)
docker system prune
```

---

## Data Management

### Prometheus Data Persistence

```bash
# Prometheus data stored in: prometheus-data volume
# Location: /var/lib/docker/volumes/beast_prometheus-data/_data/

# Check volume
docker volume inspect beast_prometheus-data | jq '.Mountpoint'

# Manually backup Prometheus data
docker run --rm -v beast_prometheus-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz -C /data .

# Restore from backup
docker run --rm -v beast_prometheus-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/prometheus-backup.tar.gz -C /data
```

### Retention Policy

```bash
# Current retention configured: 30 days (720 hours)
# Set in docker-compose.yml: --storage.tsdb.retention.time=30d

# To change retention, modify docker-compose.yml:
# command:
#   - '--storage.tsdb.retention.time=7d'    # 7 days
# Then restart: docker compose down && docker compose up -d
```

### Export Metrics

```bash
# Export all metrics to file (PromQL query)
curl 'http://localhost:9090/api/v1/query?query=.*' > metrics.json

# Export via Prometheus admin API (careful with size!)
# See: http://192.168.68.100:9090/admin
```

---

## Configuration Changes

### Update Admin Password (Grafana)

1. Edit `.env` file:
   ```bash
   GF_SECURITY_ADMIN_PASSWORD=NewPassword123
   ```

2. Restart Grafana:
   ```bash
   docker compose restart grafana
   ```

3. Login at http://localhost:3000 with new password

### Add New Prometheus Scrape Target

1. Edit `beast/monitoring/prometheus/prometheus.yml`:
   ```yaml
   scrape_configs:
     - job_name: 'new-service'
       static_configs:
         - targets: ['new-service:9100']
   ```

2. Restart Prometheus:
   ```bash
   docker compose restart prometheus
   ```

3. Check targets at: http://localhost:9090/targets

### Add New Grafana Dashboard

**Option A: Import from Grafana.com**
1. Web UI: Dashboards → New → Import
2. Enter dashboard ID (e.g., 1860 for Node Exporter)
3. Select Prometheus datasource
4. Click Import

**Option B: Add Dashboard JSON File**
1. Save JSON file to `beast/monitoring/grafana/dashboards/`
2. Restart Grafana: `docker compose restart grafana`
3. Dashboard auto-loads

### Customize Cloudflare Tunnel Routes

1. Edit `beast/cloudflare/config.yml`:
   ```yaml
   ingress:
     - hostname: new-service.yourdomain.com
       service: http://localhost:8888
   ```

2. Restart cloudflared:
   ```bash
   docker compose restart cloudflared
   ```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs prometheus

# Common solutions:
# 1. Port already in use
sudo lsof -i :9090

# 2. Permission denied (volumes)
sudo chown -R 1000:1000 beast/monitoring/

# 3. Docker daemon not running
sudo systemctl start docker
```

### High Memory Usage

```bash
# Check which service is consuming memory
docker stats --no-stream

# Reduce Prometheus retention to free space
# In docker-compose.yml: --storage.tsdb.retention.time=7d

# Or reduce query lookback in Grafana dashboards
```

### Metrics Not Updating

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq

# If targets DOWN:
# 1. Service not accessible from Docker network
# 2. Port mismatch
# 3. Service crashed

# Check service logs
docker logs node-exporter
```

### Grafana Data Missing

```bash
# Check Prometheus datasource
curl http://localhost:3000/api/datasources | jq

# Test datasource connection
curl http://localhost:3000/api/datasources/uid/prometheus/health

# Check Prometheus is responding
curl http://localhost:9090/-/healthy
```

### Cloudflare Tunnel Not Connecting

```bash
# Check tunnel status
docker logs cloudflared

# Verify tunnel credentials
ls -la ~/.cloudflared/

# Check tunnel configuration
cat beast/cloudflare/config.yml

# Restart tunnel
docker compose restart cloudflared

# Verify in Cloudflare dashboard
# https://dash.cloudflare.com/ → Access → Tunnels
```

---

## Monitoring the Monitoring Stack

### Key Metrics to Watch

```bash
# Prometheus storage size
du -sh /var/lib/docker/volumes/beast_prometheus-data/

# System resource usage
docker stats --no-stream | tail +2 | awk '{sum += $4} END {print sum}'

# Error rates
curl 'http://localhost:9090/api/v1/query?query=rate(http_requests_total{job="prometheus",status=~"5.."}[5m])'
```

### Recommended Alerts (Future Enhancement)

- Prometheus storage > 90% capacity
- Target scrape failure rate > 5%
- Docker container restarts > 0 (unexpected)
- System CPU > 80%
- System Memory > 90%

---

## Backup and Recovery

### Daily Backup Script

```bash
#!/bin/bash
BACKUP_DIR="$HOME/backups/monitoring"
mkdir -p $BACKUP_DIR

# Backup Prometheus data
docker run --rm \
  -v beast_prometheus-data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/prometheus-$(date +%Y%m%d).tar.gz -C /data .

# Backup Grafana database
docker exec grafana grafana-cli admin export-dashboard > $BACKUP_DIR/grafana-$(date +%Y%m%d).json

echo "Backup complete: $BACKUP_DIR"
```

### Full Recovery Procedure

```bash
# 1. Stop all services
docker compose down -v

# 2. Restore Prometheus data
docker volume create beast_prometheus-data
docker run --rm -v beast_prometheus-data:/data -v $BACKUP_DIR:/backup \
  alpine tar xzf /backup/prometheus-YYYYMMDD.tar.gz -C /data

# 3. Restore Grafana
docker compose up -d grafana
sleep 5
# Manual restore via UI or API

# 4. Start remaining services
docker compose up -d

# 5. Verify health
docker compose ps
curl http://localhost:9090/-/healthy
```

---

## Performance Tuning

### Reduce Prometheus Resource Usage

```yaml
# In docker-compose.yml prometheus service:
command:
  - '--config.file=/etc/prometheus/prometheus.yml'
  - '--storage.tsdb.path=/prometheus'
  - '--storage.tsdb.retention.time=7d'      # Reduce from 30d
  - '--query.max-concurrency=10'            # Limit concurrent queries
  - '--query.max-samples=1000000'           # Limit result size
```

### Optimize Scrape Intervals

```yaml
# In prometheus.yml, increase intervals for less frequent updates:
global:
  scrape_interval: 30s      # Increased from 15s
  evaluation_interval: 30s  # Increased from 15s
```

---

## Service Updates

```bash
# Update all images to latest
docker compose pull

# Only update specific service
docker compose pull prometheus

# Apply updates (restart with new images)
docker compose down
docker compose up -d
```

---

## Support & Escalation

### Phase 1: Local Diagnosis

1. Check Docker logs: `docker compose logs`
2. Verify network: `docker network ls`
3. Test endpoints: `curl http://localhost:9090/-/healthy`
4. Check disk space: `df -h`

### Phase 2: Resource Issues

1. Check memory: `docker stats`
2. Check disk: `du -sh /var/lib/docker/volumes/`
3. Reduce retention or remove old metrics
4. Increase host resources if possible

### Phase 3: Configuration Issues

1. Validate YAML files
2. Check provisioning mounts
3. Review Docker logs for parse errors
4. Manually test connectivity between services

### Phase 4: External Access Issues

1. Test local access first
2. Check Cloudflare tunnel status
3. Verify DNS records
4. Test from mobile hotspot / different network

---

**Last Updated**: 2025-10-17
**Maintained By**: DevOps / SRE Team

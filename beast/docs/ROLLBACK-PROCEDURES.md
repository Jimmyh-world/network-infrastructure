# Rollback Procedures - Beast Monitoring Infrastructure

**Document**: Emergency Rollback & Disaster Recovery
**Date Created**: 2025-10-17
**Criticality**: HIGH

---

## Per-Phase Rollback

### Phase 1: Docker Compose Base Structure

**Rollback Command:**
```bash
rm -rf ~/dev-network/beast/docker/*.yml
rm -f ~/dev-network/beast/docker/.env.example
git checkout beast/docker/
```

**Time to Rollback:** < 1 minute
**Data Loss:** None (no services running yet)

---

### Phase 2: Prometheus Stack

**Rollback Command:**
```bash
cd ~/dev-network/beast/docker
docker compose down prometheus node-exporter cadvisor
docker volume rm beast_prometheus-data
git checkout beast/docker/docker-compose.yml
git checkout beast/monitoring/prometheus/
```

**Time to Rollback:** 2-3 minutes
**Data Loss:** All Prometheus metrics since deployment (recoverable if backup exists)

---

### Phase 3: Grafana Setup

**Rollback Command:**
```bash
cd ~/dev-network/beast/docker
docker compose down grafana
docker volume rm beast_grafana-data
git checkout beast/docker/docker-compose.yml
rm -rf beast/monitoring/grafana/
```

**Time to Rollback:** 2-3 minutes
**Data Loss:** All Grafana dashboards, alerts, settings

---

### Phase 4: Portainer Setup

**Rollback Command:**
```bash
cd ~/dev-network/beast/docker
docker compose down portainer
docker volume rm beast_portainer-data
git checkout beast/docker/docker-compose.yml
```

**Time to Rollback:** 1-2 minutes
**Data Loss:** None (Portainer has no persistent user data in this setup)

---

### Phase 5: Cloudflare Tunnel

**Rollback Command:**
```bash
# Stop tunnel container
cd ~/dev-network/beast/docker
docker compose down cloudflared

# Delete Cloudflare tunnel (requires CLI)
cloudflared tunnel delete beast-tunnel

# Remove configuration
rm -f ~/dev-network/beast/cloudflare/config.yml
rm -f ~/.cloudflared/beast-tunnel.json

# Uninstall CLI (optional)
sudo apt remove cloudflared
```

**Time to Rollback:** 5-10 minutes (includes CLI uninstall)
**Data Loss:** Tunnel credentials (recreate tunnel via Cloudflare UI)

---

## Complete Stack Rollback

### Scenario: Full Infrastructure Failure/Reset

```bash
#!/bin/bash
# Complete rollback script

echo "🔴 BEGINNING FULL STACK ROLLBACK..."

# 1. Stop all services
echo "Stopping services..."
cd ~/dev-network/beast/docker
docker compose down -v

# 2. Remove all volumes
echo "Removing data volumes..."
docker volume rm beast_prometheus-data beast_grafana-data beast_portainer-data 2>/dev/null || true

# 3. Reset git (optional - comment out if you want to keep configuration)
echo "Resetting configuration to last commit..."
cd ~/dev-network
git checkout beast/

# 4. Delete entire beast directory (DESTRUCTIVE)
# UNCOMMENT ONLY IF YOU WANT COMPLETE WIPE
# rm -rf ~/dev-network/beast/

# 5. Cloudflare cleanup (requires manual verification)
echo "⚠️  Manual Cloudflare cleanup needed:"
echo "  1. Visit: https://dash.cloudflare.com/"
echo "  2. Go to: Access → Tunnels"
echo "  3. Delete: beast-tunnel (if it exists)"
echo "  4. Remove DNS records (if created)"

echo "✅ ROLLBACK COMPLETE"
echo "Total time: ~5 minutes"
```

**Time to Complete:** ~5 minutes
**Data Loss:** Everything (complete reset)
**Recovery:** Rebuild from git history

---

## Partial Rollback Scenarios

### Scenario A: Rollback Monitoring Only (Keep Portainer & Tunnel)

```bash
cd ~/dev-network/beast/docker

# Stop monitoring services
docker compose down prometheus node-exporter cadvisor grafana

# Remove monitoring volumes
docker volume rm beast_prometheus-data beast_grafana-data

# Keep running:
# - portainer (container management)
# - cloudflared (external access)

# Restart isolated services
docker compose up -d portainer cloudflared
```

**Result:** Can still manage containers but lose metrics visualization
**Time:** 3-5 minutes

---

### Scenario B: Rollback Tunnel Only (Keep Internal Monitoring)

```bash
cd ~/dev-network/beast/docker

# Stop tunnel
docker compose down cloudflared

# Manually delete tunnel via Cloudflare dashboard
# https://dash.cloudflare.com/ → Access → Tunnels → Delete

# Keep internal services running:
docker compose up -d

# Services still accessible internally at:
# - Grafana: http://192.168.68.100:3000
# - Portainer: https://192.168.68.100:9443
# - Prometheus: http://192.168.68.100:9090
```

**Result:** Monitor infrastructure locally but no external access
**Time:** 2-3 minutes

---

### Scenario C: Upgrade Service (Rolling Update)

**Example: Update Grafana without downtime**

```bash
cd ~/dev-network/beast/docker

# 1. Pull new image
docker compose pull grafana

# 2. Restart single service (handled by compose)
docker compose up -d grafana

# 3. Verify health
sleep 10
curl http://localhost:3000/api/health | jq '.database'

# 4. If update fails, rollback
docker compose down grafana
# Previous version still available (retained in docker cache)
docker compose up -d grafana
```

**Downtime:** 30-60 seconds (automatic restart)
**Data Loss:** None (volume persisted)

---

## Data Recovery

### Restore Prometheus Metrics

**From Backup:**
```bash
# If you have a backup file
docker volume create beast_prometheus-data
docker run --rm -v beast_prometheus-data:/data -v ~/backups:/backup \
  alpine tar xzf /backup/prometheus-20251017.tar.gz -C /data

# Restart Prometheus
docker compose down prometheus
docker compose up -d prometheus
```

**From Scratch:**
```bash
# Delete old data
docker volume rm beast_prometheus-data

# Prometheus will start fresh
docker compose up -d prometheus

# Data collection resumes immediately
# Previous metrics are lost (unavoidable)
```

---

### Restore Grafana Dashboards

**From Grafana Backup:**
```bash
# If you exported dashboards via API
docker exec grafana grafana-cli admin import-dashboard /var/lib/grafana/dashboards/dashboard.json
```

**From Provided Dashboards:**
```bash
# Pre-provided dashboards are in git
docker compose down grafana
docker volume rm beast_grafana-data
docker compose up -d grafana

# Dashboards auto-load from provisioning config
curl http://localhost:3000/api/search | jq '.[] | {title}'
```

---

## Verification After Rollback

```bash
# 1. Check services running
docker compose ps

# 2. Verify network
docker network ls | grep monitoring

# 3. Check volumes remain (or removed if full rollback)
docker volume ls | grep beast

# 4. Validate configuration
test -f docker-compose.yml && echo "✓ docker-compose.yml exists"
test -f .env && echo "✓ .env exists"

# 5. Test connectivity
curl -s http://localhost:9090/-/healthy
curl -s http://localhost:3000/api/health | jq '.database'
```

---

## Prevention & Safety

### Backup Strategy

```bash
# Daily backup of Prometheus
0 2 * * * cd ~/dev-network/beast/docker && \
  docker run --rm -v beast_prometheus-data:/data -v ~/backups:/backup \
  alpine tar czf /backup/prom-$(date +\%Y\%m\%d).tar.gz -C /data . 2>/dev/null

# Weekly full snapshot (optional)
0 3 * * 0 docker run --rm \
  -v beast_prometheus-data:/p \
  -v beast_grafana-data:/g \
  -v ~/backups:/b \
  alpine tar czf /b/full-$(date +\%Y\%m\%d).tar.gz -C / p g
```

### Git Safety

```bash
# Ensure .env not in git
echo ".env" >> .gitignore
echo "*.json" >> .gitignore

# Verify
git check-ignore .env
git check-ignore beast/cloudflare/tunnel-credentials.json
```

### Access Control

```bash
# Restrict docker socket (host security)
sudo usermod -aG docker $USER
sudo systemctl restart docker

# Verify only necessary users have docker access
getent group docker
```

---

## Disaster Recovery Timeline

| Time | Action | Owner |
|------|--------|-------|
| T+0s | Alert received | On-call SRE |
| T+30s | Assess severity | SRE + Team Lead |
| T+2m | Decision: Continue or Rollback | Team Lead |
| T+5m | Rollback executed | SRE |
| T+8m | Verification complete | SRE |
| T+10m | Service restored | SRE |
| T+30m | Incident review started | Team Lead |

---

## Escalation Matrix

### Level 1: Service Degradation
- **Symptoms:** Slow response, occasional errors
- **Action:** Restart service, check logs
- **Rollback:** Only if restart fails
- **Escalate if:** Issue persists after restart

### Level 2: Service Down (Non-Critical)
- **Symptoms:** Service returns 500 errors
- **Action:** Check container health, restart
- **Rollback:** Yes if restart fails
- **Escalate if:** Affects multiple services

### Level 3: Data Loss Risk
- **Symptoms:** Storage full, permission denied
- **Action:** Immediate rollback + investigation
- **Rollback:** Yes, immediately
- **Escalate if:** Data integrity compromised

### Level 4: Security Breach
- **Symptoms:** Unauthorized access, credential leak
- **Action:** Immediate full reset, credential rotation
- **Rollback:** Yes, to last known good state
- **Escalate if:** External systems affected

---

## Testing Rollback Procedure

**Recommended**: Test rollback procedure monthly

```bash
#!/bin/bash
# Monthly rollback drill

echo "🧪 STARTING ROLLBACK DRILL..."

# 1. Backup current state
docker run --rm \
  -v beast_prometheus-data:/data \
  -v ~/drill-backup:/backup \
  alpine tar czf /backup/pre-drill-prom.tar.gz -C /data .

# 2. Execute rollback
./rollback-procedures.sh

# 3. Verify clean state
docker compose ps | wc -l
docker volume ls | grep beast | wc -l

# 4. Restore from backup
docker volume create beast_prometheus-data
docker run --rm \
  -v beast_prometheus-data:/data \
  -v ~/drill-backup:/backup \
  alpine tar xzf /backup/pre-drill-prom.tar.gz -C /data

# 5. Restart services
docker compose up -d

echo "✅ DRILL COMPLETE"
```

---

**Last Updated**: 2025-10-17
**Next Review**: 2025-11-17
**Owner**: DevOps Team

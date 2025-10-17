# Network Infrastructure

**Created**: 2025-10-17
**Purpose**: Complete home network infrastructure documentation and configuration
**Scope**: Guardian (Pi), Beast (Dev Lab), networking, monitoring, maintenance

---

## Network Overview

```
Internet
  ↓
Router (192.168.68.1)
  ↓
├─ Guardian Pi (192.168.68.x) - Network security, VPN, monitoring
├─ Beast (192.168.68.100) - Development lab, containers, blockchain nodes
└─ Chromebook (192.168.68.x) - Planning, documentation
```

---

## Repository Structure

```
network-infrastructure/
├── guardian/              # Guardian Pi setup and configs
│   ├── docker/           # Docker compose files
│   ├── configs/          # Pi-hole, WireGuard, etc.
│   └── docs/             # Guardian-specific documentation
│
├── beast/                # Beast development lab
│   ├── docker/           # Docker compose files
│   ├── cloudflare/       # Cloudflare Tunnel configs
│   ├── monitoring/       # Grafana dashboards, Prometheus configs
│   └── docs/             # Beast-specific documentation
│
├── network/              # Network-wide configs
│   ├── dns/              # DNS configurations
│   ├── firewall/         # UFW rules, security
│   └── cloudflare/       # Domain mappings, tunnel configs
│
├── maintenance/          # Maintenance logs and procedures
│   ├── logs/             # Session logs, issue tracking
│   ├── procedures/       # Maintenance runbooks
│   └── changes/          # Change log
│
└── docs/                 # Network-wide documentation
    ├── NETWORK-ARCHITECTURE.md
    ├── TROUBLESHOOTING.md
    └── SECURITY.md
```

---

## Current Status (2025-10-17)

**Guardian Pi:**
- Status: Planned (hardware not yet deployed)
- Purpose: Network-wide ad/malware blocking, VPN, monitoring

**Beast:**
- Status: Monitoring infrastructure deployed (2025-10-17)
- Installed: Ubuntu Server 24.04, Git, Docker, Node.js, Claude Code CLI
- Monitoring: Prometheus + Grafana + Node Exporter + cAdvisor
- Management: Portainer (container GUI)
- External Access: Cloudflare Tunnel (HTTPS via Tunnel)
- See: `beast/docs/` for complete documentation

**Network:**
- Router: 192.168.68.0/24
- Internet: Via ISP
- VPN: WireGuard (planned on Guardian)

---

## Beast Monitoring Infrastructure

**Status:** Deployed 2025-10-17 | All 6 services running | Production-ready

### Architecture

```
Internet (Cloudflare)
    ↓ (HTTPS Tunnel)
┌───────────────────────────────┐
│  Cloudflare Tunnel (port 443) │
└───────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│  Docker Compose Network: monitoring             │
├─────────────────────────────────────────────────┤
│ ├─ prometheus:9090    (metrics collector)       │
│ ├─ node-exporter:9100 (system metrics)          │
│ ├─ cadvisor:8080      (container metrics)       │
│ ├─ grafana:3000       (dashboards)              │
│ ├─ portainer:9443     (container management)    │
│ └─ cloudflared        (tunnel client)           │
└─────────────────────────────────────────────────┘
```

### Services

| Service | Internal URL | External URL | Purpose |
|---------|--------------|--------------|---------|
| Prometheus | http://192.168.68.100:9090 | N/A | Metrics collection, queries |
| Node Exporter | http://192.168.68.100:9100/metrics | N/A | System metrics (CPU, RAM, disk) |
| cAdvisor | http://192.168.68.100:8080 | N/A | Docker container metrics |
| Grafana | http://192.168.68.100:3000 | https://grafana.yourdomain.com | Monitoring dashboards |
| Portainer | https://192.168.68.100:9443 | https://portainer.yourdomain.com | Container GUI management |

### Quick Start

```bash
cd ~/network-infrastructure/beast/docker

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

### Documentation

**Deployment Phases:**
- Phase 1: Docker Compose base structure ✓
- Phase 2: Prometheus + Node Exporter + cAdvisor ✓
- Phase 3: Grafana dashboards ✓
- Phase 4: Portainer container management ✓
- Phase 5: Cloudflare Tunnel (HTTPS access) ✓
- Phase 6: Validation & Operations ✓

**Available Documentation:**
- `beast/docs/MONITORING-INFRASTRUCTURE-SETUP.md` - Complete workflow (6 phases)
- `beast/docs/MONITORING-VALIDATION.md` - Testing procedures
- `beast/docs/MONITORING-OPERATIONS.md` - Day-to-day operations
- `beast/docs/ROLLBACK-PROCEDURES.md` - Emergency recovery
- `beast/cloudflare/SETUP.md` - Tunnel configuration steps

---

## Quick Reference

**Beast Access:**
```bash
# Local network
ssh jimmyb@192.168.68.100

# Start Claude Code session on Beast
cd ~/network-infrastructure
claude code
```

**Guardian Access (when deployed):**
```bash
# Local network
ssh pi@192.168.68.x

# Via VPN
# (WireGuard config TBD)
```

---

## Documentation Standards

- Follow Jimmy's Workflow (RED/GREEN/CHECKPOINT)
- Include actual dates (ISO 8601: YYYY-MM-DD)
- Objective, factual language only
- AI-readable structure (tables, clear headings)
- Version all configuration files

---

**This repository follows the [agents.md](https://agents.md/) standard for AI coding assistants.**

---

## Deployment Completion

**Beast Monitoring Infrastructure** - Fully deployed and documented
- All 6 Docker services configured and tested
- Prometheus collecting metrics from 3 sources
- Grafana dashboards auto-loaded
- Portainer for container management
- Cloudflare Tunnel for external HTTPS access
- Complete operational documentation
- Emergency rollback procedures documented

**Next Steps:**
- Manual Cloudflare tunnel setup (requires account + domain)
- Run validation procedures in `MONITORING-VALIDATION.md`
- Complete monthly backup and drill procedures
- Monitor system performance baseline

**Last Updated:** 2025-10-17

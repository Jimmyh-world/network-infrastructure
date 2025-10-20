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
dev-network/
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

## Current Status (2025-10-19)

**Guardian Pi:**
- Status: Planned (hardware arriving 2025-10-20)
- Purpose: Network-wide ad/malware blocking, VPN, monitoring, always-on services
- Design Docs: `~/dev-guardian/` (architecture and planning)
- Deployment Configs: `guardian/` (this repository)

**Beast:**
- Status: Monitoring + Scraper infrastructure deployed (2025-10-17)
- Installed: Ubuntu Server 24.04, Git, Docker, Node.js, Claude Code CLI
- Monitoring: Prometheus + Grafana + Node Exporter + cAdvisor
- Management: Portainer (container GUI)
- Article Scraping: ydun-scraper (trafilatura-based extraction)
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
│ Cloudflare Tunnel (host proc) │
│ d2d710e7-94cd-41d8-9979...   │
│ 4x edge connections (arn02,06,07)│
└───────────────────────────────┘
    ↓ (localhost routing)
┌─────────────────────────────────────────────────┐
│  Docker Compose Network: monitoring             │
├─────────────────────────────────────────────────┤
│ ├─ prometheus:9090     (metrics collector)       │
│ ├─ node-exporter:9100 (system metrics)          │
│ ├─ cadvisor:8080      (container metrics)       │
│ ├─ grafana:3000       (dashboards)              │
│ ├─ portainer:9443     (container management)    │
│ └─ ydun-scraper:5000  (article extraction)      │
└─────────────────────────────────────────────────┘
```

### Services

| Service | Internal URL | External URL | Purpose |
|---------|--------------|--------------|---------|
| Prometheus | http://192.168.68.100:9090 | N/A | Metrics collection, queries |
| Node Exporter | http://192.168.68.100:9100/metrics | N/A | System metrics (CPU, RAM, disk) |
| cAdvisor | http://192.168.68.100:8080 | N/A | Docker container metrics |
| Grafana | http://192.168.68.100:3000 | https://grafana.kitt.agency | Monitoring dashboards |
| Portainer | https://192.168.68.100:9443 | https://portainer.kitt.agency (⚠️) | Container GUI management |
| Ydun Scraper | http://192.168.68.100:5000 | https://scrape.kitt.agency | Article extraction microservice |

### Cloudflare Tunnel (Host-Based)

**Important:** The cloudflared tunnel runs directly on the Beast host (not in Docker).

**Start tunnel:**
```bash
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
```

**Stop tunnel:**
```bash
pkill -f "cloudflared tunnel"
```

**Check status:**
```bash
cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7
```

See `beast/cloudflare/TUNNEL-HOST-DEPLOYMENT.md` for complete tunnel management guide.

### Quick Start

```bash
cd ~/dev-network/beast/docker

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

**Start tunnel (separate process):**
```bash
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
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
- `beast/cloudflare/TUNNEL-HOST-DEPLOYMENT.md` - Host-based tunnel management
- `beast/cloudflare/SETUP.md` - Tunnel configuration steps

---

## Quick Reference

**Beast Access:**
```bash
# Local network
ssh jimmyb@192.168.68.100

# Start Claude Code session on Beast
cd ~/dev-network
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

**Beast Monitoring + Scraper Infrastructure** - Fully deployed and operational
- All 7 Docker services configured and tested:
  - Prometheus, Node Exporter, cAdvisor (monitoring)
  - Grafana (dashboards), Portainer (management)
  - ydun-scraper (article extraction)
  - cloudflared (Tunnel client)
- Prometheus collecting metrics from 3 sources
- Grafana dashboards auto-loaded
- Portainer for container management
- **Ydun Scraper functional**: Extracts articles via Cloudflare Tunnel
- Cloudflare Tunnel deployed and active (4 edge connections)
- Complete operational documentation
- Emergency rollback procedures documented

**Ydun Scraper Details:**
- External URL: https://scrape.kitt.agency/scrape
- Internal URL: http://localhost:5000/scrape
- Framework: Python Flask with trafilatura article extraction
- API Format: JSON POST with URLs array
- Performance: 2+ URLs per second, <500ms per article
- Status: ✅ Operational, ready for Mundus integration

**Available Documentation:**
- `beast/docs/YDUN-SCRAPER-DEPLOYMENT.md` - Complete 8-phase workflow
- `beast/docs/MUNDUS-INTEGRATION.md` - Mundus integration guide
- `beast/docs/MONITORING-INFRASTRUCTURE-SETUP.md` - Monitoring workflow

**Next Steps:**
- Integrate ydun-scraper with Mundus Supabase edge functions
- Configure advanced Prometheus metrics for scraper (optional)
- Set up automated backups
- Monitor system performance baseline

---

## Mundus Editor Platform - Staging Deployment

**Status:** Infrastructure Ready (2025-10-20) | Awaiting Application Deployment
**Domain:** web3studio.dev
**Staging URL:** https://mundus.web3studio.dev
**Purpose:** Beast staging environment for Mundus Editor Platform before Render.com production

### Infrastructure Components

**Cloudflare Tunnel (Dedicated):**
- Tunnel: mundus-tunnel (87b661c8-75f9-4113-abf6-f02125a4aaa4)
- Domain: web3studio.dev
- Route: mundus.web3studio.dev → Beast:8081
- Status: ✅ HEALTHY (4 active connections) - Running on Beast

**Beast Deployment:**
- Location: `beast/docker/mundus/`
- Services: hello-world-test (tracer bullet), then full monorepo
- Repository: https://github.com/Jimmyh-world/m-e-p (main branch)
- Status: ⚪ Infrastructure Ready (awaiting m-e-p repository with hello-world service)

### Deployment Stages

**Stage 1: Tracer Bullet (Next)**
- Deploy hello-world-test service
- Validate pipeline: GitHub → Beast → Cloudflare → Internet
- Test: https://mundus.web3studio.dev

**Stage 2: Final Assembly**
- Deploy backend (Express TypeScript API)
- Deploy editor-frontend (React + Vite)
- Deploy digest-frontend (React + Vite)
- Integration testing on Beast

**Stage 3: Live Testing**
- Client validation on Beast staging
- Iterate based on feedback
- Performance testing

**Stage 4: Production Migration**
- Deploy to Render.com (when Beast validation complete)
- Update DNS or use Render domains
- Decommission Beast staging (optional)

### Available Documentation

- `beast/cloudflare/config-web3studio.yml` - Tunnel configuration
- `beast/docs/MUNDUS-TUNNEL-SETUP.md` - Cloudflare Tunnel setup instructions
- `beast/docs/MUNDUS-DEPLOYMENT-SPEC.md` - Complete deployment workflow
- `beast/docker/mundus/docker-compose.yml` - Service orchestration (stub)

### Quick Start (For Beast Execution)

**1. Set up Cloudflare Tunnel:**
```bash
# See: beast/docs/MUNDUS-TUNNEL-SETUP.md
cloudflared tunnel create mundus-tunnel
cloudflared tunnel route dns mundus-tunnel mundus.web3studio.dev
# Start tunnel with config-web3studio.yml
```

**2. Deploy services:**
```bash
# See: beast/docs/MUNDUS-DEPLOYMENT-SPEC.md
cd ~
git clone https://github.com/Jimmyh-world/m-e-p.git
cd ~/dev-network/beast/docker/mundus
docker compose up -d
```

**3. Test:**
```bash
curl https://mundus.web3studio.dev
```

**Last Updated:** 2025-10-20

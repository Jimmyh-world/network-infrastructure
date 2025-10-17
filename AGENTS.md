# Network Infrastructure - AI Assistant Guidelines

**Repository**: network-infrastructure
**Purpose**: Home network infrastructure (Guardian + Beast + networking)
**Created**: 2025-10-17

---

## Core Development Principles

1. **KISS** - Keep It Simple, Stupid
2. **TDD** - Test-Driven Development (validate everything)
3. **SOC** - Separation of Concerns
4. **DRY** - Don't Repeat Yourself
5. **Documentation Standards** - Factual, dated, objective
6. **Jimmy's Workflow** - RED/GREEN/CHECKPOINT (MANDATORY)
7. **YAGNI** - You Ain't Gonna Need It
8. **Fix Now** - Never defer known issues

---

## Repository Context

This repository manages:
- **Guardian Pi**: Network security (Pi-hole, WireGuard, monitoring)
- **Beast**: Development lab (Docker, blockchain nodes, services)
- **Network**: DNS, firewall, Cloudflare Tunnel
- **Maintenance**: Logs, procedures, change tracking

---

## Technology Stack

**Infrastructure:**
- Ubuntu Server 24.04 LTS (Beast)
- Raspberry Pi OS (Guardian)
- Docker + Docker Compose
- Cloudflare Tunnel

**Monitoring:**
- Grafana (dashboards)
- Prometheus (metrics)
- Node Exporter (system metrics)
- cAdvisor (container metrics)

**Networking:**
- WireGuard (VPN)
- Pi-hole (DNS/ad blocking)
- UFW (firewall)

---

## Development Workflow

### Using Jimmy's Workflow

All infrastructure changes MUST follow RED/GREEN/CHECKPOINT:

- 🔴 **RED (IMPLEMENT)**: Deploy/configure infrastructure
- 🟢 **GREEN (VALIDATE)**: Run explicit validation commands
- 🔵 **CHECKPOINT**: Document rollback procedure, mark complete

### Example Workflow

```markdown
## 🔴 RED - Deploy Grafana

cd ~/network-infrastructure/beast/docker
docker compose up -d grafana

## 🟢 GREEN - Validate

curl http://localhost:3000/api/health
docker ps | grep grafana
docker logs grafana

## 🔵 CHECKPOINT

Status: ✅ COMPLETE
Rollback: docker compose stop grafana && docker compose rm -f grafana
Time to rollback: 30 seconds
```

---

## Security Guidelines

**Never Commit:**
- API keys or tokens
- Passwords or secrets
- SSL certificates or private keys
- Cloudflare Tunnel credentials

**Always:**
- Use `.env` files for secrets (gitignored)
- Document what secrets are needed
- Use strong passwords
- Keep systems updated

---

## Common Commands

**Beast:**
```bash
# SSH access
ssh jimmyb@192.168.68.100

# Docker operations
cd ~/network-infrastructure/beast/docker
docker compose up -d
docker compose logs -f
docker ps

# System health
htop
df -h
docker stats
```

**Guardian (future):**
```bash
# SSH access
ssh pi@192.168.68.x

# Pi-hole
pihole status
pihole -g  # Update gravity

# WireGuard
sudo systemctl status wg-quick@wg0
sudo wg show
```

---

**This document follows the [agents.md](https://agents.md/) standard.**

**Last Updated:** 2025-10-17

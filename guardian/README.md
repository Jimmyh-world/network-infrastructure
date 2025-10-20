# Guardian - Deployment Configurations

**Design Repository:** `~/dev-guardian/` (architecture, planning, setup guides)
**Purpose:** Deployment configs and runtime files for Guardian Pi 5
**Status:** Hardware DEPLOYED (2025-10-19) - Pi-hole running, Tier 1 expansion needed

---

## Directory Structure

```
guardian/
├── docker/         # Docker Compose files for Guardian services
├── configs/        # Actual configuration files (Pi-hole, WireGuard, etc.)
├── docs/           # Deployment-specific documentation
└── scripts/        # Deployment and maintenance scripts
```

---

## Architecture

For architecture, planning, and design documentation, see:

**Primary:** `~/dev-guardian/docs/GUARDIAN-2.0-ARCHITECTURE.md`

This directory contains only deployment artifacts and configs.

---

## Relationship

```
dev-guardian/                    → Design, specs, planning (Chromebook)
dev-network/guardian/ → Deployment, configs, runtime (Guardian Pi 5)
```

**Design decisions:** Made in `~/dev-guardian/`
**Deployment configs:** Stored here in `~/dev-network/guardian/`

---

## Status

**Hardware:** Guardian Pi 5 (8GB RAM) deployed at 192.168.68.10 ✅
**Services Running:** Pi-hole (DNS filtering, Beast using it) ✅
**Current Phase:** Tier 1 partially deployed (see ~/dev-guardian/STATUS.md)

**This Directory:** Empty (needs population with deployment configs)
**Next:** Create Docker Compose files and configs for remaining Tier 1 services:
- Suricata (IDS, deep packet inspection)
- ntopng (traffic monitoring)
- Grafana/Prometheus (monitoring dashboards)
- Tailscale (VPN mesh networking) ⭐ Chosen over WireGuard
- Alert system

**VPN Decision (2025-10-20):** Using **Tailscale** instead of WireGuard for VPN mesh networking. See `docs/TAILSCALE-EVALUATION.md` for rationale.

**Complete Architecture:** See `~/dev-guardian/docs/GUARDIAN-2.0-ARCHITECTURE.md`

---

**For complete Guardian architecture and planning, see `~/dev-guardian/`**

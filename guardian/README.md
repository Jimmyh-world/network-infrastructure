# Guardian - Deployment Configurations

**Design Repository:** `~/dev-guardian/`
**Purpose:** Deployment configs and runtime files for Guardian Pi 5
**Status:** Awaiting hardware deployment (Deco XE75 arriving 2025-10-20)

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

**Current:** Empty (hardware pending)
**Next:** Populate with deployment configs when Phase 1 begins (post 2025-10-20)

---

**For complete Guardian architecture and planning, see `~/dev-guardian/`**

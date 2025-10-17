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
- Status: Initial setup in progress
- Installed: Ubuntu Server 24.04, Git, Docker, Node.js, Claude Code CLI
- Next: Cloudflare Tunnel + monitoring stack

**Network:**
- Router: 192.168.68.0/24
- Internet: Via ISP
- VPN: WireGuard (planned on Guardian)

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

**Last Updated:** 2025-10-17

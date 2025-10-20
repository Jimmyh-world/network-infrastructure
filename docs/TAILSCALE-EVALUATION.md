# Tailscale VPN Evaluation & Deployment Plan

**Created:** 2025-10-20
**Status:** Evaluated - Ready for Deployment
**Decision:** Use Tailscale instead of WireGuard for VPN mesh networking

---

## Executive Summary

Tailscale provides zero-config VPN mesh networking for the three-machine architecture (Chromebook, Guardian, Beast). It eliminates the need for port forwarding, provides automatic NAT traversal, and includes MagicDNS for seamless access.

**Recommendation:** Deploy Tailscale on Guardian as part of Tier 1 Core Security.

---

## What is Tailscale?

**Type:** WireGuard-based VPN mesh networking service
**Protocol:** WireGuard (modern, fast, secure)
**Architecture:** Peer-to-peer mesh with coordination server
**Cost:** Free tier (up to 100 devices, 1 admin)
**Website:** https://tailscale.com/

### How It Works

```
Traditional VPN (Hub-and-Spoke):
Chromebook → VPN Server → Beast
                ↓
            Guardian

Tailscale (Mesh):
Chromebook ←→ Beast
    ↕          ↕
Guardian ←→ (direct connections)
```

**Key Difference:** All devices connect directly to each other (peer-to-peer), not through a central server.

---

## Why Tailscale Over WireGuard

| Feature | Tailscale | Self-Hosted WireGuard | Winner |
|---------|-----------|----------------------|---------|
| **Setup Time** | 5 minutes | 1-2 hours | 🏆 Tailscale |
| **Port Forwarding** | Not required | Required (UDP 51820) | 🏆 Tailscale |
| **NAT Traversal** | Automatic (STUN/DERP) | Manual configuration | 🏆 Tailscale |
| **Mesh Networking** | Built-in | Requires full-mesh config | 🏆 Tailscale |
| **MagicDNS** | Built-in (`ssh beast`) | Manual /etc/hosts | 🏆 Tailscale |
| **Mobile Apps** | Native (iOS, Android, ChromeOS) | Third-party apps | 🏆 Tailscale |
| **ACLs** | Web UI + gitops | Manual iptables | 🏆 Tailscale |
| **Zero Config** | Yes | No | 🏆 Tailscale |
| **Maintenance** | Zero (managed service) | Regular updates needed | 🏆 Tailscale |
| **Privacy** | Coordination server sees metadata | Fully self-hosted | 🏆 WireGuard |
| **Control** | Limited to Tailscale features | Complete control | 🏆 WireGuard |
| **Cost** | Free (100 devices) | Free | 🟰 Tie |

**Verdict:** Tailscale wins on ease of use, WireGuard wins on privacy. For this use case (home lab, development), **Tailscale is the better choice**.

---

## Why Tailscale Over Deco XE75 Built-in VPN

| Feature | Tailscale | Deco Built-in VPN | Winner |
|---------|-----------|------------------|---------|
| **NAT Traversal** | Excellent (STUN/DERP) | Poor (often fails) | 🏆 Tailscale |
| **Network Type** | Mesh (all devices talk) | Hub-and-spoke only | 🏆 Tailscale |
| **MagicDNS** | Yes (`ssh beast`) | No (must use IPs) | 🏆 Tailscale |
| **ACLs** | Fine-grained per-device | Basic firewall only | 🏆 Tailscale |
| **Subnet Routing** | Yes (access entire LAN) | Not available | 🏆 Tailscale |
| **Exit Nodes** | Yes (route all traffic) | Yes (built-in) | 🟰 Tie |
| **Mobile Apps** | Excellent (native) | Deco app (basic) | 🏆 Tailscale |
| **Setup** | 5 minutes | 30 minutes | 🏆 Tailscale |
| **Privacy** | Tailscale sees metadata | TP-Link sees everything | 🏆 Tailscale |
| **Reliability** | Excellent | Variable | 🏆 Tailscale |

**Verdict:** Tailscale is superior in every way except requiring a separate app.

---

## Tailscale in the Three-Machine Architecture

### Current Network (Local Only)

```
Internet
  ↓
Deco XE75 Router (192.168.68.1)
  ↓
├── Chromebook (192.168.68.x)  - Development
├── Guardian Pi (192.168.68.10) - DNS, Security
└── Beast (192.168.68.100)      - Services

Access: Only works at home on local network
```

### With Tailscale (Global Access)

```
Internet
  ↓
Tailscale Coordination Server (manages mesh)
  ↓
Tailscale Mesh Network (100.x.x.x IPs):
├── Chromebook (100.x.x.1)
│   └── MagicDNS: chromebook.tail<hash>.ts.net
│
├── Guardian (100.x.x.2) [Subnet Router]
│   └── MagicDNS: guardian.tail<hash>.ts.net
│   └── Advertises: 192.168.68.0/24
│
├── Beast (100.x.x.3)
│   └── MagicDNS: beast.tail<hash>.ts.net
│
└── Your Phone (100.x.x.4)
    └── MagicDNS: phone.tail<hash>.ts.net

Access: Works from anywhere (coffee shop, office, traveling)
```

**Key Feature:** Guardian advertises the entire home network (192.168.68.0/24), so you can access ANY device through the Tailscale VPN.

---

## Use Cases

### 1. Remote Development from Chromebook

**Scenario:** Working from coffee shop, need to deploy to Beast

**Without Tailscale:**
```bash
# Can't access Beast at all (not on home network)
# Must use Cloudflare Tunnel for limited services
```

**With Tailscale:**
```bash
# From anywhere in the world:
ssh beast
cd ~/dev-network/beast/docker
docker compose ps
docker compose logs -f
```

### 2. Mobile SSH Access

**Scenario:** Client reports Mundus staging is down, you're out running errands

**Without Tailscale:**
```bash
# Can't SSH from phone
# Can't check Docker logs
# Must wait until home
```

**With Tailscale:**
```bash
# From phone (Termius app):
ssh beast
docker compose restart mundus-hello-world
curl http://localhost:8081/api/health
# Fixed! Client notified.
```

### 3. Access Internal Services

**Scenario:** Need to check Prometheus metrics or Pi-hole stats remotely

**Without Tailscale:**
```bash
# Only Grafana exposed via Cloudflare Tunnel
# Can't access Prometheus, Pi-hole, Portainer, etc.
```

**With Tailscale:**
```bash
# From browser anywhere:
http://beast:9090        # Prometheus
http://guardian:80/admin # Pi-hole
http://beast:9443        # Portainer
```

### 4. Three-Machine Coordination

**Scenario:** Chromebook orchestrates, Beast executes, Guardian monitors

**Without Tailscale:**
```bash
# Only works at home
# Can't coordinate when traveling
```

**With Tailscale:**
```bash
# From Chromebook anywhere:
ssh beast "git pull && docker compose up -d"
ssh guardian "pihole -c"
# Full coordination from anywhere
```

---

## Deployment Architecture

### Recommended: Guardian as Primary Node

**Role:** Guardian acts as subnet router and always-on gateway

```
Guardian Pi Responsibilities:
├── Tier 1 Core Security:
│   ├── Pi-hole (DNS filtering) ✅
│   ├── Suricata (IDS) ⚪
│   ├── ntopng (traffic analysis) ⚪
│   ├── Grafana/Prometheus (monitoring) ⚪
│   └── Tailscale (VPN mesh) ⭐ NEW
│
└── Always-on (5-12W power):
    ├── Never sleeps (24/7 availability)
    ├── Subnet router (advertises 192.168.68.0/24)
    └── Exit node (optional - route all traffic through home)
```

**Why Guardian?**
- ✅ Always-on (Pi never sleeps)
- ✅ Low power (can run VPN 24/7 cheaply)
- ✅ Aligns with Guardian's "edge agent" role
- ✅ Beast can sleep, VPN stays active

**Resource Usage:**
- RAM: ~50MB
- CPU: <5% (idle), ~10-15% (active traffic)
- Network: Minimal (only coordination packets when idle)

---

## Installation Steps

### Phase 1: Basic Mesh (15 minutes)

**Install Tailscale on all three machines:**

```bash
# Chromebook (Debian container)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Beast (Ubuntu Server)
ssh jimmyb@192.168.68.100
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh

# Guardian (Raspberry Pi OS)
ssh jamesb@192.168.68.10
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh
```

**Result:** All three machines can SSH to each other via MagicDNS.

### Phase 2: Subnet Routing (5 minutes)

**Enable subnet routing on Guardian:**

```bash
# On Guardian
sudo tailscale up --advertise-routes=192.168.68.0/24 --accept-routes --ssh

# In Tailscale admin console (web UI):
# → Machines → guardian → Edit route settings
# → Approve subnet route: 192.168.68.0/24
```

**Result:** Access entire home network through Tailscale (192.168.68.0/24).

### Phase 3: Mobile Access (5 minutes)

**Install on phone:**
1. Install Tailscale app (iOS/Android)
2. Login with same account
3. Done! Access `ssh beast` from phone.

**Optional: Install SSH client:**
- Termius (recommended)
- Blink Shell (iOS, power users)
- JuiceSSH (Android)

### Phase 4: ACLs (Optional, 15 minutes)

**Lock down access with Access Control Lists:**

```json
// Example: Phone can only SSH to Beast/Guardian, not access services
{
  "acls": [
    {
      "action": "accept",
      "src": ["phone"],
      "dst": ["beast:22", "guardian:22"]
    },
    {
      "action": "accept",
      "src": ["chromebook"],
      "dst": ["*:*"]
    }
  ]
}
```

---

## Security Considerations

### What Tailscale Sees (Privacy)

**Coordination Server knows:**
- ✅ Your email address (account)
- ✅ Device names and IPs (metadata)
- ✅ When devices are online (presence)
- ✅ Which devices are connected to which

**Coordination Server DOES NOT see:**
- ❌ Actual traffic content (end-to-end encrypted)
- ❌ What services you're accessing
- ❌ SSH commands you run
- ❌ Files you transfer

**Encryption:** All traffic is end-to-end encrypted with WireGuard (ChaCha20-Poly1305).

### Threat Model Assessment

**For home lab development:**
- ✅ Tailscale is appropriate (convenience > privacy)
- ✅ No sensitive data in transit (development environment)
- ✅ Easier than self-hosting coordination server

**If you need absolute privacy:**
- Use Headscale (self-hosted Tailscale coordination server)
- Use plain WireGuard (full self-hosting)

**Current recommendation:** Tailscale free tier is sufficient.

### Security Best Practices

**On machines:**
```bash
# Enable Tailscale SSH (no key management)
sudo tailscale up --ssh

# Enable MagicDNS
# (automatically enabled)

# Enable key expiry (re-auth every 180 days)
# Default behavior, good security hygiene
```

**On mobile:**
1. Enable biometric auth (Face ID/fingerprint)
2. Enable "Network Lock" (kill switch if VPN drops)
3. Use ACLs to restrict phone access

**In Tailscale admin:**
1. Enable device approval (manually approve new devices)
2. Set up ACLs (fine-grained access control)
3. Enable logging (audit trail)

---

## Integration with Existing Infrastructure

### Tailscale + Cloudflare Tunnel (Complementary)

**Cloudflare Tunnel:** For public services (Mundus staging, Grafana)
**Tailscale:** For private infrastructure access (SSH, Docker, development)

```
External Users (Public):
  → Cloudflare Tunnel → Beast services
      └─ Use for: Client testing, public dashboards

You (Private):
  → Tailscale VPN → Full infrastructure access
      └─ Use for: Development, SSH, internal services
```

**No conflict - both work simultaneously.**

### Tailscale + Pi-hole (Compatible)

**MagicDNS + Pi-hole work together:**

```
DNS Resolution Flow:
1. Tailscale MagicDNS resolves: beast, guardian, chromebook
2. Pi-hole resolves: everything else + blocks ads/malware
3. Both work seamlessly
```

**Configuration:**
```bash
# On Guardian with Pi-hole + Tailscale:
sudo tailscale up --accept-dns=false
# This prevents Tailscale from overriding Pi-hole DNS
```

---

## Performance

### Latency

**Direct connection (same location):**
- Local network: <1ms
- Tailscale (same location): 1-2ms (minimal overhead)

**Remote connection (different location):**
- Without Tailscale: N/A (can't connect)
- Tailscale direct: Your internet latency (STUN works)
- Tailscale DERP relay: +10-50ms (when direct fails)

**Verdict:** Fast enough for all use cases (SSH, Docker, development).

### Bandwidth

**Throughput:**
- WireGuard overhead: ~5% (very efficient)
- Practical speeds: 100+ Mbps (limited by home upload speed)

**For your use cases:**
- SSH: <1 Mbps (no issue)
- Docker logs: <10 Mbps (no issue)
- File transfer: Limited by home upload (~20-50 Mbps typical)

---

## Cost Analysis

### Tailscale Free Tier

**Includes:**
- ✅ Up to 100 devices
- ✅ 1 admin user
- ✅ MagicDNS
- ✅ Subnet routing
- ✅ ACLs
- ✅ Mobile apps

**Limits:**
- ⚠️ 1 admin (can't share admin access)
- ⚠️ Basic support (community forums)

**For your setup:** Free tier is perfect (3 devices + phone = 4 total).

### Tailscale Personal Pro ($48/year)

**Adds:**
- Multiple admins
- Priority support
- Custom DERP servers
- Longer session duration

**Needed?** No. Free tier covers all your use cases.

---

## Comparison to Alternatives

### Tailscale vs. Headscale (Self-Hosted)

**Headscale:** Open-source Tailscale coordination server you host

**Pros:**
- ✅ Full privacy (you own coordination server)
- ✅ No Tailscale account needed

**Cons:**
- ❌ Must maintain coordination server
- ❌ No official mobile apps (must use Tailscale apps with custom server)
- ❌ Less stable (community project)

**Verdict:** Overkill for home lab. Stick with Tailscale.

### Tailscale vs. ZeroTier

**ZeroTier:** Alternative mesh VPN service

**Tailscale advantages:**
- ✅ Based on WireGuard (faster, modern)
- ✅ Better NAT traversal
- ✅ Simpler setup
- ✅ Better mobile apps

**Verdict:** Tailscale is better.

---

## Deployment Plan

### Tier 1 Integration (Recommended)

**Add Tailscale to Guardian Tier 1 Core Security:**

```
Tier 1 Services:
├── Pi-hole (DNS filtering) - 100MB RAM ✅
├── Suricata (IDS) - 200MB RAM ⚪
├── ntopng (traffic) - 150MB RAM ⚪
├── Prometheus (metrics) - 200MB RAM ⚪
├── Grafana (dashboards) - 100MB RAM ⚪
└── Tailscale (VPN mesh) - 50MB RAM ⭐

Total: ~800MB RAM (6.2GB available for Tier 2)
```

### Deployment Timeline

**Week 1 (with Deco XE75 setup):**
- Day 1: Install Deco XE75, configure network
- Day 1: Install Tailscale on all three machines
- Day 1: Test basic mesh connectivity
- Day 2: Configure subnet routing on Guardian
- Day 2: Test mobile access
- Day 3: Set up ACLs (optional)

**Estimated effort:** 30 minutes (Tailscale only)

---

## Rollback Procedure

**If Tailscale causes issues:**

```bash
# Stop Tailscale
sudo systemctl stop tailscaled

# Disable autostart
sudo systemctl disable tailscaled

# Uninstall (if needed)
sudo apt remove tailscale

# Network continues working normally
# (Tailscale is additive, doesn't replace existing network)
```

**Risk level:** Low (Tailscale runs alongside existing network, doesn't replace it).

---

## Next Steps

1. **Review this document** - Understand Tailscale architecture
2. **Deco XE75 setup** - Configure router first
3. **Install Tailscale** - Deploy on all three machines (30 min)
4. **Test connectivity** - Verify mesh works
5. **Configure subnet routing** - Enable access to entire LAN
6. **Install on phone** - Mobile access
7. **Update Guardian architecture docs** - Add Tailscale to Tier 1

---

## References

- **Official site:** https://tailscale.com/
- **Documentation:** https://tailscale.com/kb/
- **GitHub:** https://github.com/tailscale/tailscale
- **Security whitepaper:** https://tailscale.com/security/
- **WireGuard protocol:** https://www.wireguard.com/

---

**Decision:** Deploy Tailscale on Guardian as part of network setup (with Deco XE75).

**Last Updated:** 2025-10-20

# Access Methods & Credentials

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Purpose:** Centralized guide for accessing all infrastructure services and locating credentials

---

## Quick Reference

| Service | Local Network | External HTTPS | Authentication |
|---------|--------------|----------------|----------------|
| **Grafana** | http://192.168.68.100:3000 | https://grafana.kitt.agency | admin / (see .env) |
| **Scraper** | http://192.168.68.100:5000 | https://scrape.kitt.agency | None (open API) |
| **Portainer** | https://192.168.68.100:9443 | ⚠️ 502 error | Set on first access |
| **Prometheus** | http://192.168.68.100:9090 | N/A (internal only) | None |
| **Node Exporter** | http://192.168.68.100:9100 | N/A (internal only) | None |
| **cAdvisor** | http://192.168.68.100:8080 | N/A (internal only) | None |
| **Beast SSH** | ssh jimmyb@192.168.68.100 | N/A | SSH key: beast@dev-lab |

---

## Access Methods by Location

### From Chromebook (Development Machine)

**External HTTPS (Preferred for general access):**
```bash
# Grafana dashboards
https://grafana.kitt.agency

# Scraper health check
https://scrape.kitt.agency/health

# Scraper API
curl -X POST https://scrape.kitt.agency/scrape \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com/article"]}'
```

**Local Network (Preferred for development/debugging):**
```bash
# Grafana
http://192.168.68.100:3000

# Scraper
http://192.168.68.100:5000

# Prometheus
http://192.168.68.100:9090

# Portainer
https://192.168.68.100:9443

# Node Exporter
http://192.168.68.100:9100/metrics

# cAdvisor
http://192.168.68.100:8080
```

**SSH Access:**
```bash
# Connect to Beast
ssh jimmyb@192.168.68.100

# Execute remote command
ssh jimmyb@192.168.68.100 "docker compose ps"

# Copy files to/from Beast
scp localfile.txt jimmyb@192.168.68.100:~/
scp jimmyb@192.168.68.100:~/remotefile.txt ./
```

### From Beast (Direct Access)

**Local Services:**
```bash
# All services accessible via localhost
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:5000/health      # Scraper
curl http://localhost:9090/-/healthy   # Prometheus
curl http://localhost:9100/metrics     # Node Exporter
curl http://localhost:8080/healthz     # cAdvisor
```

**Docker Management:**
```bash
# Via Docker Compose
cd ~/network-infrastructure/beast/docker
docker compose ps
docker compose logs -f
docker compose restart <service>

# Via Portainer (if configured)
# https://localhost:9443

# Direct Docker commands
docker ps
docker stats
docker logs <container>
```

### From Internet (External Access)

**Via Cloudflare Tunnel:**
```bash
# Only these services exposed externally
https://grafana.kitt.agency
https://scrape.kitt.agency

# All other services internal only (security by design)
```

**Benefits:**
- ✅ HTTPS encryption (Cloudflare-managed certificates)
- ✅ No port forwarding on router (more secure)
- ✅ Access from anywhere
- ✅ DDoS protection (Cloudflare)
- ✅ Automatic certificate renewal

---

## Credentials & Authentication

### Grafana

**Access:**
- Local: http://192.168.68.100:3000
- External: https://grafana.kitt.agency

**Credentials:**
- **Username:** `admin`
- **Password:** See `.env` file on Beast

**Get Password:**
```bash
# On Beast
cat ~/network-infrastructure/beast/docker/.env | grep GF_SECURITY_ADMIN_PASSWORD

# Or from Chromebook via SSH
ssh jimmyb@192.168.68.100 "cat ~/network-infrastructure/beast/docker/.env | grep GF_SECURITY_ADMIN_PASSWORD"
```

**Security Notes:**
- Password generated with `openssl rand -base64 32`
- Stored in `.env` file (gitignored, not in version control)
- Should be changed from initial password on first login
- HTTPS enforced for external access

**Reset Password:**
```bash
# On Beast
cd ~/network-infrastructure/beast/docker
docker compose exec grafana grafana-cli admin reset-admin-password <new-password>

# Update .env file
nano .env  # Update GF_SECURITY_ADMIN_PASSWORD

# Restart Grafana
docker compose restart grafana
```

### Portainer

**Access:**
- Local: https://192.168.68.100:9443
- External: ⚠️ 502 error (self-signed cert issue)

**Initial Setup:**
1. Navigate to https://192.168.68.100:9443 (first time)
2. Set admin password (12+ characters recommended)
3. Create local environment (Docker socket already connected)

**Credentials:**
- **Username:** `admin`
- **Password:** Set by you on first access

**Security Notes:**
- Self-signed certificate (browser will warn - this is expected)
- Accept certificate exception on first access
- Password stored in Portainer data volume
- Not exposed externally (by design)

### ydun-scraper

**Access:**
- Local: http://192.168.68.100:5000
- External: https://scrape.kitt.agency

**Authentication:** None (open API)

**Security Considerations:**
- No authentication currently (intended for internal use)
- External access via Cloudflare Tunnel
- Consider adding API key authentication for production
- Rate limiting recommended

**Example Implementation (Future):**
```typescript
// Add to edge function
if (req.headers.get("X-API-Key") !== Deno.env.get("SCRAPER_API_KEY")) {
  return new Response("Unauthorized", { status: 401 });
}
```

### Beast SSH

**Access:**
```bash
ssh jimmyb@192.168.68.100
```

**Authentication:** SSH key-based (no password)

**Key Locations:**
- **Private key (Chromebook):** `~/.ssh/id_rsa` or `~/.ssh/id_ed25519`
- **Public key (Beast):** `~/.ssh/authorized_keys`
- **Key name:** beast@dev-lab

**Verify Key:**
```bash
# On Chromebook - check private key exists
ls -la ~/.ssh/id_rsa

# On Beast - check authorized key
ssh jimmyb@192.168.68.100 "cat ~/.ssh/authorized_keys"
```

**Add New Key (if needed):**
```bash
# On Chromebook - generate new key
ssh-keygen -t ed25519 -C "beast@dev-lab"

# Copy public key to Beast
ssh-copy-id jimmyb@192.168.68.100

# Test
ssh jimmyb@192.168.68.100 "hostname"
```

### Cloudflare Tunnel

**Credentials Location (Beast):**
- **Origin Certificate:** `~/.cloudflared/cert.pem`
- **Tunnel Credentials:** `~/.cloudflared/d2d710e7-94cd-41d8-9979-0519fa1233e7.json`

**Permissions:**
```bash
# Should be 600 (owner read/write only)
ls -la ~/.cloudflared/
# -rw------- cert.pem
# -rw------- d2d710e7-94cd-41d8-9979-0519fa1233e7.json
```

**Fix Permissions (if needed):**
```bash
chmod 600 ~/.cloudflared/*
```

**Cloudflare Account:**
- **Domain:** kitt.agency
- **Tier:** Free
- **Dashboard:** https://dash.cloudflare.com/

---

## Network Architecture

### Physical Network Topology

```
Internet
  ↓
Router (192.168.68.1)
  ├── Chromebook (192.168.68.x) - Development, documentation
  ├── Beast (192.168.68.100)    - Infrastructure, services
  └── [Guardian Pi] (planned)    - DNS, VPN, security
```

### External Access Flow

```
User Browser (anywhere in the world)
  ↓
DNS: *.kitt.agency → Cloudflare nameservers
  ↓
Cloudflare Edge Network (nearest PoP)
  ↓
Cloudflare Tunnel (encrypted connection)
  ├── grafana.kitt.agency → Beast:3000
  ├── scrape.kitt.agency → Beast:5000
  └── portainer.kitt.agency → Beast:9443 (502 error)
  ↓
Beast Host (192.168.68.100)
  ↓
Docker Containers (monitoring network)
```

### Internal Network Access

```
Chromebook (192.168.68.x)
  ↓
Local Network (192.168.68.0/24)
  ↓
Beast (192.168.68.100)
  ├── Docker exposes ports to host
  └── Host exposes ports to network
```

**Key Point:** Docker services bind to `0.0.0.0`, making them accessible from any device on local network, not just localhost.

---

## Use Case: When to Use Which Method

### Development & Debugging
**Use:** Local network access (http://192.168.68.100:PORT)

**Why:**
- ✅ Faster (no tunnel overhead)
- ✅ Direct connection (no Cloudflare proxy)
- ✅ Access to all services (including internal-only)
- ✅ Full Docker logs available

**Example:**
```bash
# Check if service is actually running
curl http://192.168.68.100:3000/api/health

# View real-time logs
ssh jimmyb@192.168.68.100
docker compose logs -f grafana
```

### Production Usage
**Use:** External HTTPS (https://*.kitt.agency)

**Why:**
- ✅ Works from anywhere (not just local network)
- ✅ HTTPS encryption
- ✅ No VPN required
- ✅ Automatic certificate management

**Example:**
```bash
# Access Grafana dashboards from coffee shop
https://grafana.kitt.agency

# Call scraper from Supabase edge function
fetch("https://scrape.kitt.agency/scrape", {...})
```

### Emergency Access
**Use:** SSH to Beast + local Docker CLI

**Why:**
- ✅ Direct system access
- ✅ Full Docker control
- ✅ Log inspection
- ✅ Service restart capability

**Example:**
```bash
# SSH to Beast
ssh jimmyb@192.168.68.100

# Check what's wrong
docker compose ps
docker compose logs --tail 100

# Restart problematic service
docker compose restart grafana
```

### API Integration
**Use:** External HTTPS for production, local for development

**Why:**
- ✅ Production: Reliable, secure, works from Supabase/cloud
- ✅ Development: Fast, no rate limits, easy debugging

**Example:**
```typescript
// Development
const scraperUrl = "http://192.168.68.100:5000/scrape";

// Production
const scraperUrl = "https://scrape.kitt.agency/scrape";
```

---

## Troubleshooting Access Issues

### Problem: Can't Access Grafana

**Symptom:** Browser shows "Can't connect" or timeout

**Diagnosis:**
```bash
# 1. Is Beast reachable?
ping 192.168.68.100

# 2. Is Grafana container running?
ssh jimmyb@192.168.68.100 "docker compose ps | grep grafana"

# 3. Is Grafana responding locally?
ssh jimmyb@192.168.68.100 "curl -I http://localhost:3000/api/health"

# 4. Is port 3000 open?
ssh jimmyb@192.168.68.100 "netstat -tulpn | grep 3000"

# 5. Is Cloudflare Tunnel working?
ssh jimmyb@192.168.68.100 "ps aux | grep cloudflared"
```

**Solutions:**
- If Beast unreachable: Check network, router, Beast power
- If container not running: `docker compose up -d grafana`
- If not responding: Check logs `docker compose logs grafana`
- If port not open: Check docker-compose.yml port mapping
- If tunnel down: Restart tunnel (see TUNNEL-HOST-DEPLOYMENT.md)

### Problem: External HTTPS Not Working

**Symptom:** 502 Bad Gateway or timeout on https://*.kitt.agency

**Diagnosis:**
```bash
# 1. Is Cloudflare Tunnel connected?
ssh jimmyb@192.168.68.100 "cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7"

# 2. Are services running locally?
ssh jimmyb@192.168.68.100 "curl http://localhost:3000/api/health"
ssh jimmyb@192.168.68.100 "curl http://localhost:5000/health"

# 3. Check tunnel logs
ssh jimmyb@192.168.68.100 "tail -50 /tmp/cloudflared.log"

# 4. Check DNS
nslookup grafana.kitt.agency
```

**Solutions:**
- If tunnel not connected: Restart tunnel
- If services not running: Start Docker services
- If DNS not resolving: Wait for propagation (up to 5 minutes)
- If logs show errors: Check config.yml, credentials

### Problem: SSH Connection Refused

**Symptom:** `ssh: connect to host 192.168.68.100 port 22: Connection refused`

**Diagnosis:**
```bash
# 1. Is Beast reachable?
ping 192.168.68.100

# 2. Is SSH service running? (need physical access to Beast)
# On Beast directly:
sudo systemctl status ssh
```

**Solutions:**
- If ping fails: Check network cable, router, Beast power
- If SSH service down: `sudo systemctl start ssh` (needs physical/console access)
- If firewall blocking: `sudo ufw allow 22/tcp` (needs physical/console access)

### Problem: Wrong Password

**Symptom:** "Invalid username or password" on Grafana

**Solutions:**
```bash
# Get current password
ssh jimmyb@192.168.68.100 "cat ~/network-infrastructure/beast/docker/.env | grep GF_SECURITY_ADMIN_PASSWORD"

# Reset password
ssh jimmyb@192.168.68.100 "cd ~/network-infrastructure/beast/docker && docker compose exec grafana grafana-cli admin reset-admin-password newpassword123"
```

### Problem: Certificate Warning

**Symptom:** Browser warns about untrusted certificate (Portainer)

**Solution:**
- This is expected for Portainer (self-signed certificate)
- Click "Advanced" → "Proceed" (or browser equivalent)
- This is safe for local network access
- DO NOT accept for external/untrusted sites

---

## Security Considerations

### External Exposure

**What's Exposed:**
- ✅ Grafana (read-only dashboards with authentication)
- ✅ Scraper API (stateless, no sensitive data)
- ❌ Prometheus (internal only - metrics)
- ❌ Node Exporter (internal only - system info)
- ❌ cAdvisor (internal only - container info)
- ❌ Portainer (internal only - Docker control)

**Why Limited Exposure:**
- Minimize attack surface
- Prevent unauthorized metrics access
- Protect infrastructure management tools
- Only expose what's necessary for external use

### Authentication Layers

**Layer 1: Network Isolation**
- Internal services only accessible on local network
- No port forwarding on router
- Beast behind firewall

**Layer 2: Cloudflare Tunnel**
- Encrypted tunnel (no exposed ports)
- DDoS protection
- Rate limiting (Cloudflare-managed)
- SSL/TLS encryption

**Layer 3: Application Authentication**
- Grafana: Username/password
- Portainer: Username/password
- Scraper: None (consider adding API key)

**Layer 4: SSH Key-Based Auth**
- No password authentication
- Private key required
- Key-based only (sshd_config)

### Best Practices

**DO:**
- ✅ Use HTTPS for all external access
- ✅ Keep SSH keys secure (600 permissions)
- ✅ Change default passwords
- ✅ Use strong passwords (20+ characters, generated)
- ✅ Regularly update Docker images
- ✅ Monitor access logs

**DON'T:**
- ❌ Share SSH private keys
- ❌ Commit .env files to Git
- ❌ Use weak passwords (e.g., "password123")
- ❌ Expose all services externally
- ❌ Disable firewall
- ❌ Use default credentials

---

## Credential Storage Locations

### Chromebook (`/home/jimmyb/`)

```
~/.ssh/
├── id_rsa              # SSH private key (600)
├── id_rsa.pub          # SSH public key (644)
└── known_hosts         # Known SSH hosts (644)

~/network-infrastructure/
└── (no secrets - all gitignored)
```

### Beast (`/home/jimmyb/`)

```
~/.ssh/
├── authorized_keys     # SSH public keys (600)
└── known_hosts         # Known SSH hosts (644)

~/.cloudflared/
├── cert.pem           # Cloudflare origin cert (600)
└── d2d710e7-94cd-41d8-9979-0519fa1233e7.json  # Tunnel creds (600)

~/network-infrastructure/beast/docker/
└── .env               # Environment variables (600)
    ├── GF_SECURITY_ADMIN_PASSWORD
    ├── GF_SERVER_ROOT_URL
    └── PROMETHEUS_RETENTION
```

**All secret files are gitignored and never committed to version control.**

---

## External Service Accounts

### Cloudflare

**Account:** Personal account (free tier)
**Domain:** kitt.agency
**Dashboard:** https://dash.cloudflare.com/
**Authentication:** Email + password (2FA recommended)

**Resources:**
- DNS zone: kitt.agency
- Tunnel: beast-tunnel (d2d710e7-94cd-41d8-9979-0519fa1233e7)
- Tunnel routes: 3 (grafana, scrape, portainer)

### GitHub

**Account:** Jimmyh-world
**Repositories:** 3 private repos
- network-infrastructure
- dev-lab
- ydun-scraper

**Authentication:** SSH keys (same as Beast SSH)

---

## Quick Command Reference

### Access Services

```bash
# Grafana
open https://grafana.kitt.agency  # External
open http://192.168.68.100:3000   # Local

# Scraper
curl https://scrape.kitt.agency/health
curl http://192.168.68.100:5000/health

# Portainer
open https://192.168.68.100:9443

# Prometheus
open http://192.168.68.100:9090
```

### SSH Operations

```bash
# Connect
ssh jimmyb@192.168.68.100

# Execute command
ssh jimmyb@192.168.68.100 "command"

# Copy files
scp file.txt jimmyb@192.168.68.100:~/
scp jimmyb@192.168.68.100:~/file.txt ./

# SSH tunnel (port forwarding)
ssh -L 3000:localhost:3000 jimmyb@192.168.68.100
# Then access http://localhost:3000 on Chromebook
```

### Get Credentials

```bash
# Grafana password
ssh jimmyb@192.168.68.100 "cat ~/network-infrastructure/beast/docker/.env | grep GF_SECURITY_ADMIN_PASSWORD"

# Cloudflare credentials
ssh jimmyb@192.168.68.100 "ls -la ~/.cloudflared/"
```

---

## Related Documentation

- `beast/docs/BEAST-INFRASTRUCTURE-STATUS.md` - Complete service inventory
- `beast/cloudflare/TUNNEL-HOST-DEPLOYMENT.md` - Tunnel management
- `docs/NEXT-SESSION-START-HERE.md` - Quick start guide
- `beast/docs/MONITORING-OPERATIONS.md` - Day-to-day operations

---

**This document is the central reference for all access methods and credentials.**

---

**Last Updated:** 2025-10-17

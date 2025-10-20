# Mundus Cloudflare Tunnel Setup - Beast Infrastructure

**Created**: 2025-10-20
**Machine**: Beast (192.168.68.100)
**Domain**: web3studio.dev
**Subdomain**: mundus.web3studio.dev
**Purpose**: Staging environment for Mundus Editor Platform

---

## Overview

This document provides instructions for Beast to set up a dedicated Cloudflare Tunnel for the Mundus Editor Platform staging environment.

**Why Separate Tunnel:**
- Isolates mundus staging from production services (kitt.agency)
- Easier to manage and tear down
- Clean separation of concerns
- Can be deleted without affecting monitoring infrastructure

---

## Prerequisites

- [x] Cloudflared CLI installed on Beast
- [x] web3studio.dev domain active in Cloudflare
- [x] HTTPS enabled on web3studio.dev
- [ ] Sufficient disk space on Beast (>5GB recommended)

---

## Phase 1: Create New Tunnel

### Step 1.1: Authenticate (if not already done)

**Note:** If Beast is already authenticated with Cloudflare (from kitt.agency setup), skip this step.

```bash
# Only run if not already authenticated
cloudflared tunnel login
# Browser will open - select web3studio.dev domain
```

### Step 1.2: Create mundus-tunnel

```bash
# Create dedicated tunnel for mundus
cloudflared tunnel create mundus-tunnel

# Expected output:
# Tunnel credentials written to /home/jimmyb/.cloudflared/[TUNNEL_ID].json
# Copy the TUNNEL_ID from the output
```

### Step 1.3: List Tunnels to Verify

```bash
cloudflared tunnel list

# Expected output should show:
# ID                                   NAME            CREATED
# d2d710e7-94cd-41d8-9979-0519fa1233e7 beast-tunnel    ...
# [NEW_TUNNEL_ID]                      mundus-tunnel   ...
```

---

## Phase 2: Update Configuration

### Step 2.1: Update config-web3studio.yml

**File location:** `~/dev-network/beast/cloudflare/config-web3studio.yml`

```bash
# Edit the config file
cd ~/dev-network
nano beast/cloudflare/config-web3studio.yml

# Replace [TUNNEL_ID_TO_BE_CREATED] with actual tunnel ID from Step 1.2
# Replace [TUNNEL_ID].json with actual credentials filename
```

**Example after update:**
```yaml
tunnel: abc123de-45fg-67hi-89jk-lmnopqrstuv0
credentials-file: /home/jimmyb/.cloudflared/abc123de-45fg-67hi-89jk-lmnopqrstuv0.json
```

### Step 2.2: Verify Configuration

```bash
# Validate YAML syntax
cat ~/dev-network/beast/cloudflare/config-web3studio.yml

# Check credentials file exists
ls -la ~/.cloudflared/*.json
```

---

## Phase 3: Create DNS Route

### Step 3.1: Route mundus.web3studio.dev to Tunnel

```bash
# Create DNS CNAME record pointing to tunnel
cloudflared tunnel route dns mundus-tunnel mundus.web3studio.dev

# Expected output:
# Successfully created DNS route for mundus.web3studio.dev
```

### Step 3.2: Verify DNS Route

```bash
# List all routes
cloudflared tunnel route list

# Verify with DNS lookup (may take 1-2 minutes)
nslookup mundus.web3studio.dev
# Expected: CNAME pointing to tunnel
```

---

## Phase 4: Start Tunnel

### Step 4.1: Test Tunnel Configuration

```bash
# Test config without starting tunnel
cloudflared tunnel --config ~/dev-network/beast/cloudflare/config-web3studio.yml ingress validate

# Expected: Configuration is valid
```

### Step 4.2: Start Tunnel (Background Process)

**Note:** This runs the tunnel as a background process. For production, consider systemd service.

```bash
cd ~/dev-network/beast

# Start tunnel in background
nohup cloudflared tunnel --config cloudflare/config-web3studio.yml run > /tmp/cloudflared-mundus.log 2>&1 &

# Save process ID for later
echo $! > /tmp/cloudflared-mundus.pid
```

### Step 4.3: Verify Tunnel is Running

```bash
# Check process
ps aux | grep "cloudflared.*mundus"

# Check logs
tail -f /tmp/cloudflared-mundus.log
# Expected: "Registered tunnel connection" messages

# Check tunnel status in Cloudflare dashboard
# Navigate to: Cloudflare Dashboard → Zero Trust → Access → Tunnels
# mundus-tunnel should show as HEALTHY
```

---

## Phase 5: Test End-to-End

### Step 5.1: Wait for Service Deployment

**Note:** At this stage, no service is running on port 8081 yet. This is expected.

```bash
# Check if anything is listening on port 8081
netstat -tuln | grep 8081
# Expected: No output (nothing listening yet)
```

### Step 5.2: Test Tunnel Routing (After Service Deployment)

**This step will work AFTER hello-world service is deployed**

```bash
# From Beast (local test)
curl http://localhost:8081
# Expected: Service response (after deployment)

# From external network (or Chromebook)
curl https://mundus.web3studio.dev
# Expected: Service response routed through Cloudflare
```

---

## Managing the Tunnel

### Check Tunnel Status

```bash
# List running tunnels
cloudflared tunnel list

# Check specific tunnel info
cloudflared tunnel info mundus-tunnel

# View tunnel logs
tail -f /tmp/cloudflared-mundus.log
```

### Stop Tunnel

```bash
# Find and kill the process
pkill -f "cloudflared.*mundus"

# Or use saved PID
kill $(cat /tmp/cloudflared-mundus.pid)
```

### Restart Tunnel

```bash
# Stop first
pkill -f "cloudflared.*mundus"

# Start again
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config-web3studio.yml run > /tmp/cloudflared-mundus.log 2>&1 &
echo $! > /tmp/cloudflared-mundus.pid
```

---

## Troubleshooting

### Tunnel Not Connecting

```bash
# Check credentials file exists
ls -la ~/.cloudflared/*.json

# Verify tunnel ID in config matches credentials file
grep "tunnel:" ~/dev-network/beast/cloudflare/config-web3studio.yml
ls ~/.cloudflared/ | grep ".json"

# Check Cloudflare account has tunnel
cloudflared tunnel list
```

### DNS Not Resolving

```bash
# Check DNS route exists
cloudflared tunnel route list | grep mundus

# Force DNS refresh (may take 1-5 minutes)
nslookup mundus.web3studio.dev 8.8.8.8

# Check Cloudflare dashboard
# Verify CNAME record exists for mundus.web3studio.dev
```

### Port Conflicts

```bash
# Check what's using port 8081
netstat -tuln | grep 8081

# If needed, update port in:
# 1. cloudflare/config-web3studio.yml (service: http://localhost:XXXX)
# 2. docker/mundus/docker-compose.yml (ports: "XXXX:80")
```

---

## Next Steps

After tunnel is set up and verified:

1. **Deploy hello-world service** (tracer bullet test)
   - See: `beast/docs/MUNDUS-DEPLOYMENT-SPEC.md`
   - Service will run on port 8081
   - Test: `curl https://mundus.web3studio.dev`

2. **Deploy full m-e-p services** (after tracer bullet passes)
   - Backend, frontends, etc.
   - May need additional subdomains (api.mundus.web3studio.dev, etc.)

3. **Client testing** (live validation on Beast)
   - Share URL: https://mundus.web3studio.dev
   - Gather feedback
   - Iterate on Beast before Render.com deployment

4. **Production deployment** (when Beast testing complete)
   - Deploy to Render.com
   - Update DNS or use Render domains
   - Decommission Beast staging (optional)

---

## Rollback

**To completely remove mundus tunnel:**

```bash
# Stop tunnel process
pkill -f "cloudflared.*mundus"

# Delete DNS route
cloudflared tunnel route delete mundus.web3studio.dev

# Delete tunnel
cloudflared tunnel delete mundus-tunnel

# Remove credentials
rm ~/.cloudflared/[MUNDUS_TUNNEL_ID].json

# Clean up logs
rm /tmp/cloudflared-mundus.log /tmp/cloudflared-mundus.pid
```

---

**Document Status**: Ready for Beast Execution
**Next Step**: Beast executes Phase 1 - Create New Tunnel
**Dependencies**: web3studio.dev domain active in Cloudflare

---

**Last Updated**: 2025-10-20

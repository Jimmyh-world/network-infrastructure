# Cloudflare Tunnel - Host-Based Deployment

**Created:** 2025-10-17
**Type:** Host process (not Docker container)
**Rationale:** Direct localhost access without Docker network abstraction
**Status:** Production-ready

---

## Why Host-Based?

The cloudflared tunnel runs directly on the Beast host (not in a Docker container) for these reasons:

1. **Credential Access:** Easier access to ~/.cloudflared credentials without volume mounts
2. **Localhost Routing:** Direct access to localhost:PORT without Docker bridge network complexities
3. **User Permissions:** No container user permission issues (non-root containers vs. credentials)
4. **Simplicity:** One less container to manage and troubleshoot
5. **Reliability:** Avoids Docker networking abstraction layer between tunnel and local services

---

## Current Configuration

**Tunnel ID:** `d2d710e7-94cd-41d8-9979-0519fa1233e7`
**Tunnel Name:** `beast-tunnel`
**Config File:** `~/dev-network/beast/cloudflare/config.yml`
**Credentials File:** `~/.cloudflared/d2d710e7-94cd-41d8-9979-0519fa1233e7.json`
**Origin Certificate:** `~/.cloudflared/cert.pem`
**Log File:** `/tmp/cloudflared.log`

### Ingress Routes

| Hostname | Service | Purpose |
|----------|---------|---------|
| grafana.kitt.agency | http://localhost:3000 | Grafana monitoring dashboards |
| scrape.kitt.agency | http://localhost:5000 | ydun-scraper article extraction API |
| portainer.kitt.agency | https://localhost:9443 | Portainer container management (self-signed) |
| (catch-all) | http_status:404 | Reject unknown traffic |

---

## Managing the Tunnel

### Start Tunnel

```bash
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
```

This:
- Runs as background process
- Uses configuration from `cloudflare/config.yml`
- Logs to `/tmp/cloudflared.log`
- Stays running even if terminal closes

### Stop Tunnel

```bash
pkill -f "cloudflared tunnel"
```

This gracefully terminates the tunnel process.

### Check Status

**Process check:**
```bash
ps aux | grep "cloudflared tunnel" | grep -v grep
```

Should see exactly 1 process running.

**Tunnel connection info:**
```bash
cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7
```

Expected output shows tunnel name, ID, and edge connections (typically 4 connections to different Cloudflare edge locations).

**View logs:**
```bash
tail -50 /tmp/cloudflared.log
```

Look for lines like:
- `Registered tunnel connection` - successful connection to Cloudflare edge
- `INF Tunnel server started` - tunnel is ready
- `ERR` messages - any errors (rare during normal operation)

### Test External Access

```bash
# Grafana
curl -s https://grafana.kitt.agency/api/health | jq .

# Scraper
curl -s https://scrape.kitt.agency/health | jq .

# Scraper functionality
curl -s -X POST https://scrape.kitt.agency/scrape \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"]}' | jq '.stats'
```

---

## Troubleshooting

### Multiple Processes Running

**Symptom:** `ps aux | grep cloudflared` shows multiple processes

**Solution:**
```bash
# Kill all
pkill -f "cloudflared tunnel"
sleep 2

# Verify all stopped
ps aux | grep "cloudflared tunnel" | grep -v grep

# Start one fresh
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
sleep 5

# Verify one running
ps aux | grep "cloudflared tunnel" | grep -v grep | wc -l
# Should show: 1
```

### Tunnel Not Connecting

**Symptom:** `cloudflared tunnel info` shows "no active connections"

**Solutions:**

1. Check credentials exist:
```bash
ls -la ~/.cloudflared/
# Should show:
# - cert.pem (account certificate)
# - d2d710e7-94cd-41d8-9979-0519fa1233e7.json (tunnel credentials)
```

2. Check config file is readable:
```bash
cat ~/dev-network/beast/cloudflare/config.yml
```

3. Check logs for authentication errors:
```bash
tail -50 /tmp/cloudflared.log | grep -E "ERR|auth"
```

4. Restart with fresh log:
```bash
rm -f /tmp/cloudflared.log
pkill -f "cloudflared tunnel"
sleep 2
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &
sleep 5
tail -30 /tmp/cloudflared.log
```

### 502 Bad Gateway on HTTPS

**Symptom:** Accessing `https://endpoint.kitt.agency` returns 502

**Solutions:**

1. Verify local service is running:
```bash
# Check which service is failing
docker compose ps  # in ~/dev-network/beast/docker

# Test local endpoint
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:5000/health      # Scraper
```

2. Check tunnel can reach localhost:
```bash
curl -v http://localhost:PORT/healthz
```

3. Check for port conflicts:
```bash
netstat -tulpn | grep LISTEN | grep localhost
```

4. Check logs for upstream errors:
```bash
tail -50 /tmp/cloudflared.log | grep -E "Unable to reach|502"
```

### Portainer Returns 502

**Symptom:** `https://portainer.kitt.agency` returns 502 (self-signed certificate)

**Status:** This is expected and non-critical. Portainer is still accessible locally at `https://localhost:9443`.

**Workaround:** Access Portainer locally instead:
```bash
# Open locally (requires VPN or local network access)
https://192.168.68.100:9443
```

The configuration includes `insecureSkipVerify: true` but cloudflared may still reject self-signed certificates in some versions. This does not affect Grafana or scraper access.

---

## Performance Monitoring

### Monitor Tunnel Metrics

```bash
# Real-time tunnel stats
watch -n 5 'cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7'

# Tail logs with updates
tail -f /tmp/cloudflared.log | grep -E "Registered|ERR"
```

### Monitor Service Performance

```bash
# Grafana metrics
curl -s http://localhost:9090/api/v1/query?query=up | jq '.data.result[] | {job: .metric.job, up: .value[1]}'

# System metrics
curl -s http://localhost:9100/metrics | grep -E "^node_" | head -10

# Container metrics
curl -s http://localhost:8080/api/v1/machine | jq '.stats[] | {container_name: .name, cpu_usage: .cpu_usage.total}'
```

---

## Security Considerations

### Tunnel Authentication

- **Origin Certificate:** `~/.cloudflared/cert.pem` - proves ownership of kitt.agency domain
- **Tunnel Credentials:** `~/.cloudflared/d2d710e7-94cd-41d8-9979-0519fa1233e7.json` - tunnel-specific authentication
- **TLS:** All external traffic encrypted end-to-end via Cloudflare edge

### File Permissions

Verify credentials are protected:

```bash
ls -la ~/.cloudflared/
# cert.pem and tunnel credentials should be -rw------- (600)
```

Fix if needed:
```bash
chmod 600 ~/.cloudflared/*
```

### Firewall

Beast host firewall configuration (UFW):

```bash
# Show current rules
sudo ufw status

# Cloudflared only needs outbound HTTPS (443) to Cloudflare
# Inbound ports (3000, 5000, 8080, 9090, 9100, 9443) only needed for local network
```

---

## Systemd Service (Optional)

For automatic tunnel restart on reboot, create a systemd service:

```bash
sudo tee /etc/systemd/system/cloudflared-tunnel.service > /dev/null <<EOF
[Unit]
Description=Cloudflare Tunnel for Beast Infrastructure
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=jimmyb
WorkingDirectory=/home/jimmyb/dev-network/beast
ExecStart=/usr/local/bin/cloudflared tunnel --config cloudflare/config.yml run
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-tunnel
sudo systemctl start cloudflared-tunnel

# Check status
sudo systemctl status cloudflared-tunnel

# View logs
sudo journalctl -u cloudflared-tunnel -f
```

---

## References

- **Cloudflare Tunnels:** https://developers.cloudflare.com/cloudflare-one/connections/connect-applications/
- **Config Reference:** https://developers.cloudflare.com/cloudflare-one/connections/connect-applications/install-and-setup/tunnel-guide/
- **Troubleshooting:** https://developers.cloudflare.com/cloudflare-one/troubleshooting/

---

**Last Updated:** 2025-10-17
**Maintenance:** Monitor logs regularly, restart tunnel if connection drops

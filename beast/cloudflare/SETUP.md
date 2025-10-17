# Cloudflare Tunnel Setup Instructions

## Phase 5, Step 5.1: Install Cloudflare Tunnel CLI

### Prerequisites
- Cloudflare account with access to manage tunnels
- Domain configured in Cloudflare
- Linux host with administrative access (for cloudflared installation)

### Installation Steps

```bash
# Download cloudflared binary
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# Install
sudo dpkg -i cloudflared-linux-amd64.deb

# Verify installation
cloudflared --version
```

### Authentication

```bash
# Login to Cloudflare (opens browser for authorization)
cloudflared tunnel login

# This creates credentials at: ~/.cloudflared/<user-uuid>.json
```

### Create Tunnel

```bash
# Create new tunnel named 'beast-tunnel'
cloudflared tunnel create beast-tunnel

# Verify tunnel created
cloudflared tunnel list

# Expected output shows beast-tunnel with UUID and status
```

### Configure Tunnel

```bash
# The configuration file config.yml defines routes
# See config.yml in this directory for routing setup

# Routes configured:
# - grafana.yourdomain.com -> http://localhost:3000
# - portainer.yourdomain.com -> https://localhost:9443
```

### Status Check

```bash
# Verify tunnel is created and credentials stored
ls -la ~/.cloudflared/

# Check tunnel status in Cloudflare Dashboard:
# Cloudflare → Access → Tunnels → beast-tunnel (should show HEALTHY status)
```

## Notes

- Tunnel credentials are stored locally and should NOT be committed to git
- .env file contains reference to tunnel-credentials.json location
- .gitignore excludes *.json files from beast/cloudflare/ directory
- Docker version of cloudflared runs as service in Phase 5, Step 5.3

## Next Steps

- Phase 5, Step 5.2: Configure tunnel routing
- Phase 5, Step 5.3: Add cloudflared to docker-compose.yml

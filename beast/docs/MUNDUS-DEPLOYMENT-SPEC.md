# Mundus Editor Platform - Beast Deployment Specification

**Created**: 2025-10-20
**Machine**: Beast (192.168.68.100)
**Repository**: https://github.com/ydun-code-library/Mundus-editor-application
**Branch**: main
**Domain**: mundus.web3studio.dev
**Purpose**: Staging deployment for Mundus Editor Platform

---

## Overview

This specification guides Beast in deploying Mundus Editor Platform services from the m-e-p monorepo to the staging environment at https://mundus.web3studio.dev.

**Deployment Stages:**
1. **Tracer Bullet**: hello-world-test service (validates pipeline)
2. **Final Assembly**: Full services (backend, frontends)
3. **Live Testing**: Client validation on Beast
4. **Production**: Migrate to Render.com (after Beast validation)

**Current Stage**: Tracer Bullet (hello-world-test)

---

## Prerequisites

**Before starting, verify:**

- [x] Cloudflare Tunnel for web3studio.dev configured (see: MUNDUS-TUNNEL-SETUP.md)
- [x] Tunnel running and healthy
- [x] DNS route: mundus.web3studio.dev → mundus-tunnel
- [x] Docker installed and operational
- [x] Git configured with GitHub access
- [ ] m-e-p repository accessible
- [ ] Sufficient disk space (>10GB recommended)

---

## Directory Structure on Beast

**Expected structure after deployment:**

```
/home/jimmyb/
├── dev-network/                    # Infrastructure configs (this repo)
│   └── beast/
│       ├── cloudflare/
│       │   ├── config.yml         # kitt.agency tunnel
│       │   └── config-web3studio.yml  # mundus tunnel
│       ├── docker/
│       │   ├── docker-compose.yml # Current services (monitoring, scraper)
│       │   └── mundus/            # Mundus services
│       │       └── docker-compose.yml  # Mundus-specific services
│       └── docs/
│           ├── MUNDUS-TUNNEL-SETUP.md
│           └── MUNDUS-DEPLOYMENT-SPEC.md (this file)
│
└── m-e-p/                          # Mundus monorepo (to be cloned)
    ├── services/
    │   ├── hello-world-test/      # Stage 1: Tracer bullet
    │   ├── backend/               # Stage 2: API service
    │   ├── digest-frontend/       # Stage 2: Frontend
    │   └── editor-frontend/       # Stage 2: Frontend
    ├── docker/
    │   └── services/              # Dockerfiles for each service
    └── docs/
```

---

## Phase 1: Clone m-e-p Repository

### Step 1.1: Clone Repository to Beast

```bash
# Navigate to home directory
cd ~

# Clone Mundus monorepo
git clone https://github.com/ydun-code-library/Mundus-editor-application.git

# Navigate into repo
cd Mundus-editor-application

# Verify main branch
git branch
# Expected: * main

# Check structure
ls -la
# Expected: services/, docker/, docs/, README.md, etc.
```

**Validation:**
```bash
# Verify repository cloned
test -d ~/Mundus-editor-application && echo "✅ Repository cloned"

# Verify services directory exists
test -d ~/Mundus-editor-application/services && echo "✅ Services directory present"

# Verify docker directory exists
test -d ~/Mundus-editor-application/docker && echo "✅ Docker configs present"
```

---

## Phase 2: Deploy hello-world-test (Tracer Bullet)

### Step 2.1: Verify hello-world Services Exist

```bash
cd ~/Mundus-editor-application

# Check hello-world services (2 available)
ls -la services/hello-world-test/        # Backend only
ls -la services/hello-world-fullstack/   # Full-stack React + Express
# Expected: server.js, package.json, README.md

# Check Dockerfiles
ls -la docker/services/ | grep hello
# Expected: hello-world-test.Dockerfile, hello-world-fullstack.Dockerfile
```

### Step 2.2: Create Docker Compose Configuration

**File location:** `~/dev-network/beast/docker/mundus/docker-compose.yml`

```bash
# Create mundus docker directory if not exists
mkdir -p ~/dev-network/beast/docker/mundus

# Create or edit docker-compose.yml
nano ~/dev-network/beast/docker/mundus/docker-compose.yml
```

**Configuration example (use hello-world-fullstack for full React experience):**
```yaml
version: '3.8'

networks:
  mundus:
    driver: bridge

services:
  hello-world:
    build:
      context: /home/jimmyb/Mundus-editor-application
      dockerfile: docker/services/hello-world-fullstack.Dockerfile
    container_name: mundus-hello-world
    restart: unless-stopped
    ports:
      - "8081:3000"  # Port 8081 matches Cloudflare Tunnel config
    networks:
      - mundus
```

**Note:** Adjust build context and dockerfile path based on actual m-e-p structure.

### Step 2.3: Build and Run hello-world Service

```bash
# Navigate to mundus docker directory
cd ~/dev-network/beast/docker/mundus

# Build the image
docker compose build hello-world

# Expected output:
# Building hello-world...
# Successfully built [IMAGE_ID]
# Successfully tagged mundus-hello-world:latest

# Start the service
docker compose up -d

# Expected output:
# Creating mundus-hello-world ... done
```

### Step 2.4: Verify Service Running

```bash
# Check container status
docker compose ps
# Expected: mundus-hello-world - Up

# Check container logs
docker compose logs hello-world
# Expected: No errors, service started

# Test local access
curl http://localhost:8081
# Expected: "Hello World" or similar response

# Check port binding
netstat -tuln | grep 8081
# Expected: tcp ... 0.0.0.0:8081 ... LISTEN
```

---

## Phase 3: Test Public Access

### Step 3.1: Verify Cloudflare Tunnel Routing

```bash
# Check tunnel is running
ps aux | grep "cloudflared.*mundus"
# Expected: Process running

# Check tunnel logs
tail -f /tmp/cloudflared-mundus.log
# Expected: "Registered tunnel connection" messages, no errors
```

### Step 3.2: Test External HTTPS Access

```bash
# Test from Beast (local)
curl http://localhost:8081
# Expected: Service response

# Test via Cloudflare Tunnel (external)
curl https://mundus.web3studio.dev
# Expected: Same response as local test

# Check HTTP headers
curl -I https://mundus.web3studio.dev
# Expected: HTTP 200, Cloudflare headers (CF-RAY, etc.)
```

### Step 3.3: Browser Test

**From any device (Chromebook, phone, etc.):**

1. Navigate to: https://mundus.web3studio.dev
2. Expected: "Hello World" page loads
3. Verify: No SSL/certificate warnings
4. Verify: Cloudflare proxy working (check browser network tab)

---

## Phase 4: Pipeline Validation Complete

**If all tests pass:**

✅ **Tracer Bullet SUCCESS**
- GitHub → Beast: Repository cloned
- Beast: Docker image built successfully
- Beast: Container running on port 8081
- Cloudflare Tunnel: Routing traffic correctly
- Public HTTPS: https://mundus.web3studio.dev accessible

**Next Steps:**
1. Document success in STATUS.md (m-e-p repo)
2. Proceed to Stage 2: Deploy full services (backend, frontends)
3. Update docker-compose.yml with additional services
4. Test integration between services

---

## Phase 5: Deploy Full Services (After Tracer Bullet)

**Note:** This phase executes AFTER hello-world validation passes.

### Step 5.1: Update Docker Compose for All Services

**Example configuration** (adjust based on actual services):

```yaml
version: '3.8'

networks:
  mundus:
    driver: bridge

services:
  backend:
    build:
      context: /home/jimmyb/Mundus-editor-application
      dockerfile: docker/services/backend.Dockerfile
    container_name: mundus-backend
    restart: unless-stopped
    ports:
      - "3001:3001"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - PORT=3001
      - NODE_ENV=production
    networks:
      - mundus

  editor-frontend:
    build:
      context: /home/jimmyb/Mundus-editor-application
      dockerfile: docker/services/editor-frontend.Dockerfile
    container_name: mundus-editor
    restart: unless-stopped
    ports:
      - "8082:80"
    networks:
      - mundus

  digest-frontend:
    build:
      context: /home/jimmyb/Mundus-editor-application
      dockerfile: docker/services/digest-frontend.Dockerfile
    container_name: mundus-digest
    restart: unless-stopped
    ports:
      - "8083:80"
    networks:
      - mundus

  # Optional: Nginx reverse proxy for routing
  nginx:
    image: nginx:alpine
    container_name: mundus-nginx
    restart: unless-stopped
    ports:
      - "8081:80"  # Single entry point
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - editor-frontend
      - digest-frontend
    networks:
      - mundus
```

### Step 5.2: Create Environment File

```bash
# Create .env file for secrets
cd ~/dev-network/beast/docker/mundus

nano .env

# Add necessary environment variables:
DATABASE_URL=postgresql://...
# Add other secrets as needed
```

**⚠️ Security:** Never commit .env to git

### Step 5.3: Deploy All Services

```bash
cd ~/dev-network/beast/docker/mundus

# Build all images
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps
# Expected: All services Up

# Check logs
docker compose logs -f
```

### Step 5.4: Update Cloudflare Tunnel (If Needed)

**If using subdomains** (api.mundus.web3studio.dev, editor.mundus.web3studio.dev):

```bash
# Edit tunnel config
nano ~/dev-network/beast/cloudflare/config-web3studio.yml

# Add additional routes:
# - hostname: api.mundus.web3studio.dev
#   service: http://localhost:3001
# - hostname: editor.mundus.web3studio.dev
#   service: http://localhost:8082

# Restart tunnel to pick up changes
pkill -f "cloudflared.*mundus"
cd ~/dev-network/beast
nohup cloudflared tunnel --config cloudflare/config-web3studio.yml run > /tmp/cloudflared-mundus.log 2>&1 &
```

---

## Updating Deployment (Git Pull)

**When Mundus repository is updated:**

```bash
# Pull latest changes
cd ~/Mundus-editor-application
git pull origin main

# Rebuild affected services
cd ~/dev-network/beast/docker/mundus
docker compose build [service-name]

# Restart services
docker compose restart [service-name]

# Or restart all
docker compose down && docker compose up -d
```

---

## Monitoring and Logs

### Check Service Status

```bash
cd ~/dev-network/beast/docker/mundus

# List all services
docker compose ps

# Check specific service logs
docker compose logs -f hello-world
docker compose logs -f backend

# Check all logs
docker compose logs -f
```

### Resource Usage

```bash
# Check container resource usage
docker stats

# Check disk usage
docker system df
```

### Test Endpoints

```bash
# hello-world
curl http://localhost:8081

# backend (when deployed)
curl http://localhost:3001/api/v1/health

# Test via tunnel
curl https://mundus.web3studio.dev
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker compose logs [service-name]

# Check if port is already in use
netstat -tuln | grep [PORT]

# Rebuild container
docker compose build --no-cache [service-name]
docker compose up -d [service-name]
```

### Build Fails

```bash
# Check Dockerfile path is correct
ls -la /home/jimmyb/m-e-p/docker/services/

# Check build context
cd /home/jimmyb/m-e-p
ls -la

# Try building directly with Docker
docker build -f docker/services/[service].Dockerfile -t test-build .
```

### Can't Access via HTTPS

```bash
# Check tunnel is running
ps aux | grep cloudflared

# Check tunnel logs
tail -f /tmp/cloudflared-mundus.log

# Test local access first
curl http://localhost:8081

# Check DNS
nslookup mundus.web3studio.dev
```

---

## Rollback Procedures

### Remove All Mundus Services

```bash
# Stop and remove containers
cd ~/dev-network/beast/docker/mundus
docker compose down -v

# Remove images (optional)
docker images | grep mundus
docker rmi [IMAGE_IDs]

# Clean up repository (optional)
rm -rf ~/Mundus-editor-application
```

### Keep Infrastructure, Remove Services Only

```bash
# Just stop services
cd ~/dev-network/beast/docker/mundus
docker compose stop

# Remove specific service
docker compose rm hello-world
```

---

## Success Metrics

**Tracer Bullet Complete:**
- ✅ m-e-p repository cloned to Beast
- ✅ hello-world Docker image built
- ✅ Container running on port 8081
- ✅ Local access works (http://localhost:8081)
- ✅ Public HTTPS access works (https://mundus.web3studio.dev)
- ✅ No certificate warnings
- ✅ Cloudflare proxy headers present

**Full Deployment Complete:**
- ✅ All services (backend, frontends) deployed
- ✅ Integration between services working
- ✅ Database connections working
- ✅ All endpoints accessible
- ✅ Client testing successful
- ✅ Ready for Render.com migration

---

## Next Actions After Deployment

**For Chromebook (Orchestrator):**
1. Test: https://mundus.web3studio.dev
2. Update dev-network/README.md with mundus service
3. Document any issues found
4. Plan next service deployment

**For Beast (Executor):**
1. Monitor resource usage
2. Check logs for errors
3. Keep services running
4. Report any failures back to Orchestrator

**For Client/User:**
1. Test: https://mundus.web3studio.dev
2. Provide feedback
3. Test all features
4. Approve for production migration

---

**Document Status**: Ready for Beast Execution
**Current Stage**: Repository ready with 2 hello-world services
**Dependencies**:
- MUNDUS-TUNNEL-SETUP.md (✅ tunnel configured and running)
- Mundus-editor-application/main branch (✅ services ready)

---

**Last Updated**: 2025-10-20

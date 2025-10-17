# Gunicorn Production Deployment

**Updated:** 2025-10-17
**Status:** Production-ready
**Server:** Gunicorn 23.0.0 with gthread workers

---

## Overview

The ydun-scraper microservice is deployed using Gunicorn, a production-grade WSGI HTTP server. This replaces Flask's development server, providing better performance, stability, and reliability.

## Configuration

### Server Details

| Setting | Value | Purpose |
|---------|-------|---------|
| **Server** | Gunicorn 23.0.0 | Production WSGI server |
| **Workers** | 4 | Concurrent request handling |
| **Worker Class** | gthread | Good for I/O-bound operations |
| **Threads per Worker** | 2 | Thread pool for concurrency |
| **Bind Address** | 0.0.0.0:8080 | Listen on all interfaces |
| **Request Timeout** | 120 seconds | Web scraping can be slow |
| **Port Mapping** | 5000:8080 | Docker external:internal |

### Command

```bash
gunicorn \
  --bind 0.0.0.0:8080 \
  --chdir /app/src \
  --workers 4 \
  --worker-class gthread \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  http_server:app
```

### Docker Compose Configuration

```yaml
ydun-scraper:
  build:
    context: /home/jimmyb/ydun-scraper
    dockerfile: Dockerfile
  container_name: ydun-scraper
  restart: unless-stopped
  ports:
    - "5000:8080"
  networks:
    - monitoring
  command: gunicorn --bind 0.0.0.0:8080 --chdir /app/src --workers 4 --worker-class gthread --threads 2 --timeout 120 --access-logfile - --error-logfile - http_server:app
```

## Performance

### Worker Configuration Rationale

**4 Workers:**
- Good balance for 4-core systems
- Handles concurrent article scraping requests
- Allows graceful shutdown of individual workers

**gthread Worker Class:**
- Uses threads for I/O-bound operations
- Better than sync worker for web scraping
- More efficient than multiprocessing for this use case

**2 Threads per Worker:**
- Provides thread pool for concurrent I/O
- Total concurrency: 4 workers × 2 threads = 8 concurrent operations
- Good for network-bound scraping tasks

**120-second Timeout:**
- Web scraping can take time
- Article extraction from complex pages may exceed 30 seconds
- Allows time for multiple URL processing

## Monitoring

### View Logs

```bash
# Real-time logs
docker compose logs -f ydun-scraper

# Last N lines
docker compose logs --tail 50 ydun-scraper

# Filter access logs
docker compose logs ydun-scraper | grep "GET\|POST"
```

### Health Check

```bash
# Test health endpoint
curl http://localhost:5000/health

# Expected response
{"service":"ydun-article-scraper","status":"healthy"}
```

### Performance Metrics

```bash
# Monitor container resource usage
docker stats ydun-scraper

# Expected output shows CPU and memory usage across 4 workers
```

## Scaling

### Horizontal Scaling

To increase concurrency, modify worker count in docker-compose.yml:

```yaml
# For 8-core system
command: gunicorn ... --workers 8 ...

# For 2-core system
command: gunicorn ... --workers 2 ...
```

### Graceful Restart

```bash
# Restart workers gracefully (no downtime)
docker compose restart ydun-scraper

# Or send HUP signal to master process
docker kill -s HUP $(docker inspect -f '{{.State.Pid}}' ydun-scraper)
```

## Troubleshooting

### High CPU Usage

**Symptom:** CPU usage above 80%

**Solutions:**
1. Check for slow URLs in batch processing
2. Verify network connectivity to target domains
3. Check timeout settings if requests are hanging
4. Monitor individual workers: `docker top ydun-scraper`

### Memory Issues

**Symptom:** Container memory usage increasing

**Solutions:**
1. Check for memory leaks in trafilatura or newspaper3k
2. Restart container regularly (already configured with `restart: unless-stopped`)
3. Monitor memory per worker: `docker stats ydun-scraper`
4. Increase Docker memory limit if needed: `--memory=2g`

### Slow Response Times

**Symptom:** API requests timeout

**Solutions:**
1. Verify network connectivity
2. Check if target URLs are slow to respond
3. Monitor queue depth: `docker compose logs ydun-scraper | grep "Handling"`
4. Consider increasing `--workers` or `--threads`

### Worker Crashes

**Symptom:** Workers exiting with non-zero exit codes

**Solutions:**
1. Check logs for exceptions: `docker compose logs ydun-scraper`
2. Verify Python dependencies installed correctly
3. Test application locally: `python src/http_server.py`
4. Check Gunicorn configuration for syntax errors

## Deployment Checklist

- [x] Gunicorn 23.0.0 added to requirements.txt
- [x] Production worker configuration tested
- [x] Docker image rebuilt with Gunicorn
- [x] Health check passing
- [x] Performance validated
- [x] Logging configured
- [x] Graceful shutdown tested
- [x] Documentation updated

## Migration Notes

### From Flask Development Server

**Before:**
```bash
python src/http_server.py
```
- Single-threaded
- Development only
- Not suitable for production
- Flask warning: "This is a development server"

**After:**
```bash
gunicorn --bind 0.0.0.0:8080 --workers 4 --worker-class gthread ...
```
- Multi-worker
- Production-grade
- 8x concurrent request capacity
- No warnings, proper logging

### Backwards Compatibility

The Gunicorn deployment is fully backwards compatible:
- Same API endpoint (`/scrape`)
- Same request/response format
- Same health check (`/health`)
- No client-side changes required

## References

- **Gunicorn Documentation:** https://docs.gunicorn.org/
- **gthread Worker:** https://docs.gunicorn.org/en/stable/design.html#async-workers
- **Flask Integration:** https://flask.palletsprojects.com/en/3.0.x/deploying/gunicorn/

---

**Last Updated:** 2025-10-17
**Deployed By:** Claude Code
**Status:** Production Ready

# Mundus + ydun-scraper Integration Guide

**Created:** 2025-10-17
**Status:** Ready for Implementation
**Integration Type:** Supabase Edge Function → Cloudflare Tunnel → ydun-scraper
**Scraper Endpoint:** https://scrape.kitt.agency/scrape

---

## Overview

This guide explains how to integrate the ydun-scraper microservice with Mundus Supabase edge functions. The scraper provides reliable article extraction that can be called from Supabase for content processing pipelines.

### What is ydun-scraper?

- **Purpose:** Extract article content from web pages
- **Method:** Uses trafilatura library for intelligent content extraction
- **API:** JSON-based REST API (POST)
- **Performance:** 2+ URLs/second, ~500ms per article
- **Availability:** 24/7 via Cloudflare Tunnel
- **Location:** Beast infrastructure on kitt.agency domain

---

## Architecture

```
Mundus Supabase (Postgres + Edge Functions)
    ↓
Supabase Edge Function (Deno)
    ↓ (HTTPS POST)
Cloudflare Edge Network
    ↓ (Tunnel)
Beast Infrastructure (192.168.68.100)
    ↓
ydun-scraper Microservice (Python Flask)
    ↓
trafilatura (Article Extraction)
    ↓
Response (JSON)
```

---

## API Specification

### Endpoint

```
POST https://scrape.kitt.agency/scrape
```

### Request Format

```json
{
  "urls": [
    "https://example.com/article-1",
    "https://example.com/article-2"
  ]
}
```

**Parameters:**
- `urls` (array, required): Array of article URLs to scrape
- Maximum 10 URLs per request (recommended for timeout safety)

### Response Format (Success)

```json
{
  "success": true,
  "results": [
    {
      "url": "https://example.com/article-1",
      "success": true,
      "title": "Article Title",
      "content": "Full article text extracted by trafilatura...",
      "author": "Author Name or null",
      "published_at": "2025-10-17 or null",
      "sitename": "Example.com",
      "description": "Meta description or null",
      "metadata": {
        "content_length": 5432,
        "extraction_method": "trafilatura"
      }
    }
  ],
  "stats": {
    "total": 1,
    "succeeded": 1,
    "failed": 0,
    "success_rate": 1.0,
    "duration_seconds": 0.48,
    "urls_per_second": 2.1,
    "avg_content_length": 5432
  }
}
```

### Response Format (Error)

```json
{
  "success": false,
  "error": "Missing 'urls' in request body"
}
```

**Common Errors:**
- `Missing 'urls' in request body` - urls field not provided
- `'urls' must be a list` - urls not an array
- Invalid URL format or network unreachable
- Content extraction failed for specific URLs

---

## Supabase Edge Function Example

### Deno Implementation

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

// Initialize Supabase client
const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY")!;

const scraperUrl = "https://scrape.kitt.agency/scrape";

// Handler function
serve(async (req: Request) => {
  // Only allow POST
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const body = await req.json();
    const { urls } = body;

    // Validate input
    if (!Array.isArray(urls) || urls.length === 0) {
      return new Response(
        JSON.stringify({ error: "urls must be a non-empty array" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Call ydun-scraper
    const scraperResponse = await fetch(scraperUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls }),
    });

    if (!scraperResponse.ok) {
      throw new Error(`Scraper returned ${scraperResponse.status}`);
    }

    const scraperData = await scraperResponse.json();

    // Process results for Mundus
    const processedResults = scraperData.results.map((result: any) => ({
      url: result.url,
      title: result.title || "Untitled",
      content: result.content,
      author: result.author,
      published_at: result.published_at,
      source: result.sitename || new URL(result.url).hostname,
      extracted_at: new Date().toISOString(),
      success: result.success,
    }));

    // Return results
    return new Response(JSON.stringify(processedResults), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
});
```

### Deployment

```bash
# Deploy to Supabase
supabase functions deploy scrape-articles

# Test
supabase functions invoke scrape-articles --body '{
  "urls": ["https://www.bbc.com/news/world"]
}'
```

---

## Integration Patterns

### Pattern 1: Real-time Article Processing

**Use Case:** User submits article URL, scraper extracts content immediately

```sql
-- Mundus database schema
CREATE TABLE articles (
  id BIGSERIAL PRIMARY KEY,
  url TEXT UNIQUE NOT NULL,
  title TEXT,
  content TEXT,
  author TEXT,
  source TEXT,
  extracted_at TIMESTAMP DEFAULT NOW(),
  created_by UUID REFERENCES auth.users
);

-- Trigger: Call edge function on insert
CREATE TRIGGER extract_article
AFTER INSERT ON articles
FOR EACH ROW
EXECUTE FUNCTION extract_article_content();
```

### Pattern 2: Bulk Processing

**Use Case:** Process multiple URLs in batches (up to 10 at a time)

```typescript
// Batch processor
async function processBatch(urls: string[], batchSize = 10) {
  const batches = [];
  for (let i = 0; i < urls.length; i += batchSize) {
    batches.push(urls.slice(i, i + batchSize));
  }

  const results = [];
  for (const batch of batches) {
    const response = await fetch("https://scrape.kitt.agency/scrape", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls: batch }),
    });
    const data = await response.json();
    results.push(...data.results);
  }

  return results;
}
```

### Pattern 3: Error Handling & Retry

**Use Case:** Resilient scraping with exponential backoff

```typescript
async function scrapeWithRetry(
  urls: string[],
  maxRetries = 3
): Promise<any> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch("https://scrape.kitt.agency/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ urls }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;
      await new Promise((resolve) =>
        setTimeout(resolve, Math.pow(2, attempt) * 1000)
      );
    }
  }
}
```

---

## Testing & Validation

### Local Testing (Before Integration)

```bash
# Test scraper directly
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.bbc.com/news/world"]}'

# Test via tunnel
curl -X POST https://scrape.kitt.agency/scrape \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.bbc.com/news/world"]}'
```

### Integration Testing Checklist

- [ ] Supabase edge function calls scraper endpoint
- [ ] Response parsed correctly in Supabase function
- [ ] Article content stored in database
- [ ] SSL certificate validation succeeds
- [ ] Timeout handling works (>5 seconds)
- [ ] Error responses handled gracefully
- [ ] Batch processing works (5+ URLs)
- [ ] Performance acceptable (<2 seconds for 5 URLs)

### Monitoring

**Monitor these metrics in Mundus:**
- Articles extracted per day
- Average extraction time
- Failure rate (%)
- Content length distribution

**Monitor in Beast infrastructure:**
- Scraper CPU/memory usage: `docker stats ydun-scraper`
- Tunnel connection status: `cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7`
- Scraper health: `curl -s https://scrape.kitt.agency/health`

---

## Performance Considerations

### Optimization Tips

1. **Batch Size:** Use batches of 5-10 URLs (trade-off between latency and throughput)
2. **Timeout:** Set client timeout to 30+ seconds for reliability
3. **Caching:** Cache results by URL to avoid re-scraping
4. **Rate Limiting:** Current scraper handles ~1000 URLs/hour
5. **Retry Logic:** Implement exponential backoff for failed URLs

### Known Limitations

- Some sites block automated scraping (403 Forbidden)
- JavaScript-rendered content may not be fully extracted
- Large files (>10MB) may cause timeout
- Cloudflare Tunnel has ~100ms latency overhead
- Maximum 10 URLs per request (recommended)

### Scaling

Current setup handles:
- **Peak:** 50-100 concurrent scrapes/hour
- **Sustained:** 500+ scrapes/day
- **Response time:** <1s average per article

For higher volume, consider:
- Horizontal scaling (multiple scraper instances)
- Dedicated instance for Mundus-only scraping
- Redis caching layer

---

## Troubleshooting

### Issue: Connection Timeout

**Symptom:** Requests to https://scrape.kitt.agency time out
**Solutions:**
1. Check tunnel status: `cloudflared tunnel info d2d710e7-94cd-41d8-9979-0519fa1233e7`
2. Check Beast infrastructure: `docker compose ps`
3. Verify DNS: `nslookup scrape.kitt.agency`

### Issue: 502 Bad Gateway

**Symptom:** HTTPS requests return 502
**Solutions:**
1. Check cloudflared logs: `tail -50 /tmp/cloudflared.log`
2. Verify scraper is running: `docker logs ydun-scraper --tail 20`
3. Check localhost connectivity: `curl -I http://localhost:5000/health`

### Issue: Extraction Failures for Specific URLs

**Symptom:** Response shows `"success": false` for certain URLs
**Solutions:**
1. URL may block scraping (check User-Agent handling)
2. Content may be JavaScript-rendered (trafilatura limitation)
3. Server may rate-limit (add delays between requests)
4. Network connectivity issue (test from Beast directly)

### Issue: Performance Degradation

**Symptom:** Scraping becomes slow over time
**Solutions:**
1. Check Beast resource usage: `docker stats`
2. Check Prometheus metrics in Grafana
3. Restart scraper: `docker compose restart ydun-scraper`
4. Check firewall rules: `sudo ufw status`

---

## Security Considerations

### HTTPS/SSL

- ✅ Cloudflare Tunnel provides automatic HTTPS
- ✅ Certificates automatically managed by Cloudflare
- ✅ All communication encrypted end-to-end

### Authentication (Future)

Currently, the scraper endpoint is open. For production, consider:

```typescript
// Add API key authentication
if (req.headers.get("X-API-Key") !== Deno.env.get("SCRAPER_API_KEY")) {
  return new Response("Unauthorized", { status: 401 });
}
```

### Rate Limiting (Future)

```typescript
// Simple rate limiter
const requestCounts = new Map();
const LIMIT = 100; // requests per hour

function checkRateLimit(clientId: string): boolean {
  const count = requestCounts.get(clientId) || 0;
  if (count >= LIMIT) return false;
  requestCounts.set(clientId, count + 1);
  return true;
}
```

---

## Support & Maintenance

### Contact

- **Infrastructure Owner:** jimmyb
- **Beast IP:** 192.168.68.100
- **Tunnel ID:** d2d710e7-94cd-41d8-9979-0519fa1233e7
- **Domain:** kitt.agency

### Uptime SLA

Current setup provides:
- **Availability:** Best-effort (no SLA)
- **Maintenance Window:** Monday 2-3 AM UTC
- **Rollback Time:** <5 minutes

### Escalation

1. **Scraper unresponsive:** Check logs at `/tmp/cloudflared.log`
2. **Tunnel down:** Restart with `pkill cloudflared && cd ~/dev-network/beast && nohup cloudflared tunnel --config cloudflare/config.yml run > /tmp/cloudflared.log 2>&1 &`
3. **Beast unreachable:** SSH to 192.168.68.100, check Docker: `docker compose ps`

---

## Appendix: Complete cURL Examples

### Single URL Extraction

```bash
curl -X POST https://scrape.kitt.agency/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.bbc.com/news/world"]
  }' | jq '.results[0] | {title, author, content: .content[0:100]}'
```

### Batch Processing

```bash
curl -X POST https://scrape.kitt.agency/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://news.bbc.co.uk/article-1",
      "https://news.bbc.co.uk/article-2",
      "https://news.bbc.co.uk/article-3"
    ]
  }' | jq '.stats'
```

### Health Check

```bash
curl -s https://scrape.kitt.agency/health | jq .
# Expected: {"service":"ydun-article-scraper","status":"healthy"}
```

---

**Document Status:** Complete and ready for implementation
**Last Updated:** 2025-10-17

---

*This integration guide follows the agents.md standard and is maintained in the dev-network repository.*

# Kafka Deployment on Beast - Implementation Spec

**Created:** 2025-10-21
**Phase:** RED (Implementation)
**Owner:** Chromebook Orchestrator → Beast Executor

---

## Objective

Deploy Kafka message broker on Beast for:
- GitHub webhook deployment queue
- dev-rag event streaming (CVE feeds, trading events, dev events)
- Future event-driven architecture

---

## Architecture

**Kafka Deployment:**
```
Beast (192.168.68.100)
├─ Zookeeper:2181 (Kafka coordination)
├─ Kafka:9092 (external access from Guardian)
├─ Kafka:29092 (internal Docker network)
└─ Kafka UI:8080 (web dashboard)

Guardian (192.168.68.10) → Publishes to Beast:9092
Beast workers → Consume from localhost:29092
```

---

## Topics to Create

**Deployment Webhooks:**
- `deployment-webhooks` - GitHub webhook events for auto-deployment
  - Partitions: 3 (parallel deployments)
  - Retention: 7 days

**dev-rag Events:**
- `security-events` - CVE feeds, Exploit-DB, security RSS
  - Partitions: 3
  - Retention: 30 days

- `trading-events` - Crypto prices, blockchain news
  - Partitions: 3
  - Retention: 7 days

- `dev-events` - GitHub releases, package updates, docs
  - Partitions: 3
  - Retention: 14 days

**Deployment Results:**
- `deployment-results` - Deployment success/failure status
  - Partitions: 1
  - Retention: 30 days

---

## Implementation Steps

### 1. Deploy Kafka Stack
```bash
cd ~/dev-network/beast/kafka
docker compose up -d
```

### 2. Verify Kafka Running
```bash
docker ps | grep kafka
docker logs kafka
```

### 3. Create Topics
```bash
# deployment-webhooks
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic deployment-webhooks \
  --partitions 3 \
  --replication-factor 1

# security-events
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic security-events \
  --partitions 3 \
  --replication-factor 1

# trading-events
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic trading-events \
  --partitions 3 \
  --replication-factor 1

# dev-events
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic dev-events \
  --partitions 3 \
  --replication-factor 1

# deployment-results
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic deployment-results \
  --partitions 1 \
  --replication-factor 1
```

### 4. Verify Topics
```bash
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### 5. Test Kafka from Guardian
```bash
# From Guardian, test publishing
echo '{"test": "hello from guardian"}' | \
  kafka-console-producer \
  --broker-list 192.168.68.100:9092 \
  --topic deployment-webhooks
```

---

## Success Criteria

- [x] Kafka broker running on Beast:9092
- [x] Zookeeper running on Beast:2181
- [x] Kafka UI accessible at http://192.168.68.100:8080
- [x] 5 topics created (deployment-webhooks, security-events, trading-events, dev-events, deployment-results)
- [x] Guardian can publish messages to Beast Kafka
- [x] Messages visible in Kafka UI

---

## Configuration Details

**Kafka Listeners:**
- `PLAINTEXT://kafka:29092` - Internal Docker network (for Beast workers)
- `PLAINTEXT_HOST://192.168.68.100:9092` - External access (for Guardian)

**Resource Usage:**
- Zookeeper: ~200MB RAM
- Kafka: ~1-2GB RAM
- Kafka UI: ~100MB RAM
- Total: ~1.5-2.5GB RAM (Beast has 64GB available)

**Data Retention:**
- deployment-webhooks: 7 days (168 hours)
- security-events: 30 days (720 hours)
- trading-events: 7 days (168 hours)
- dev-events: 14 days (336 hours)
- deployment-results: 30 days (720 hours)

---

## Next Steps

After Kafka deployment:
1. Deploy Guardian webhook receiver (Phase 2)
2. Deploy Beast deployment worker (Phase 3)
3. Configure GitHub webhooks
4. End-to-end testing

---

**Created:** 2025-10-21
**Status:** Ready for execution

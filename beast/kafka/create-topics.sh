#!/bin/bash
# Create Kafka topics for webhook deployment system
# Run on Beast after Kafka is deployed

set -e

KAFKA_CONTAINER="kafka"
BOOTSTRAP_SERVER="localhost:9092"

echo "Creating Kafka topics..."

# deployment-webhooks (GitHub webhook events)
echo "Creating deployment-webhooks topic..."
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --topic deployment-webhooks \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

# security-events (dev-rag CVE feeds)
echo "Creating security-events topic..."
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --topic security-events \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

# trading-events (dev-rag crypto prices)
echo "Creating trading-events topic..."
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --topic trading-events \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

# dev-events (dev-rag GitHub releases)
echo "Creating dev-events topic..."
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --topic dev-events \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

# deployment-results (deployment status)
echo "Creating deployment-results topic..."
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --topic deployment-results \
  --partitions 1 \
  --replication-factor 1 \
  --if-not-exists

echo ""
echo "Topics created successfully!"
echo ""
echo "Listing all topics:"
docker exec $KAFKA_CONTAINER kafka-topics --list --bootstrap-server $BOOTSTRAP_SERVER

echo ""
echo "Describing deployment-webhooks topic:"
docker exec $KAFKA_CONTAINER kafka-topics --describe \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --topic deployment-webhooks

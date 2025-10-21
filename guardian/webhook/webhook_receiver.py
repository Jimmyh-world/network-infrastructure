#!/usr/bin/env python3
"""
Guardian Webhook Receiver
Receives GitHub webhooks and publishes to Kafka on Beast
"""

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from kafka import KafkaProducer
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'changeme')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.68.100:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'deployment-webhooks')

# Initialize FastAPI
app = FastAPI(
    title="Guardian Webhook Receiver",
    description="Receives GitHub webhooks and queues deployments via Kafka",
    version="1.0.0"
)

# Initialize Kafka Producer (lazy, on first webhook)
kafka_producer: Optional[KafkaProducer] = None


def get_kafka_producer() -> KafkaProducer:
    """Get or create Kafka producer"""
    global kafka_producer
    if kafka_producer is None:
        logger.info(f"Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
        kafka_producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Wait for all replicas
            retries=3,
            max_in_flight_requests_per_connection=1  # Ensure ordering
        )
        logger.info("Kafka producer connected successfully")
    return kafka_producer


def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature"""
    if not signature_header:
        logger.warning("No signature header provided")
        return False

    # GitHub sends signature as: sha256=<hash>
    if not signature_header.startswith('sha256='):
        logger.warning(f"Invalid signature format: {signature_header}")
        return False

    expected_signature = signature_header.split('=')[1]

    # Compute HMAC
    mac = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    computed_signature = mac.hexdigest()

    # Constant-time comparison
    is_valid = hmac.compare_digest(computed_signature, expected_signature)

    if not is_valid:
        logger.warning("Invalid GitHub webhook signature")

    return is_valid


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Guardian Webhook Receiver",
        "status": "operational",
        "kafka": KAFKA_BOOTSTRAP_SERVERS,
        "topic": KAFKA_TOPIC
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    kafka_status = "unknown"
    try:
        producer = get_kafka_producer()
        # Test Kafka connectivity
        producer.bootstrap_connected()
        kafka_status = "connected"
    except Exception as e:
        kafka_status = f"error: {str(e)}"
        logger.error(f"Kafka health check failed: {e}")

    return {
        "status": "healthy" if kafka_status == "connected" else "degraded",
        "kafka": kafka_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None)
):
    """
    Receive GitHub webhook and queue deployment event

    GitHub webhook events we handle:
    - push (code pushed to branch)
    - release (new release published)
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify signature
    if not verify_github_signature(body, x_hub_signature_256):
        logger.error("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Extract repository info
    repo_name = payload.get('repository', {}).get('name', 'unknown')
    repo_full_name = payload.get('repository', {}).get('full_name', 'unknown/unknown')
    ref = payload.get('ref', '')
    after_commit = payload.get('after', '')

    logger.info(f"Received {x_github_event} event for {repo_full_name}")
    logger.info(f"  Ref: {ref}")
    logger.info(f"  Commit: {after_commit}")
    logger.info(f"  Delivery ID: {x_github_delivery}")

    # Only process push events to main/master branches
    if x_github_event == 'push':
        branch = ref.split('/')[-1] if ref else ''

        if branch not in ['main', 'master']:
            logger.info(f"Ignoring push to branch: {branch}")
            return {
                "status": "ignored",
                "reason": f"Not main/master branch: {branch}"
            }

        # Create deployment event
        deployment_event = {
            "event_type": "deployment",
            "repo_name": repo_name,
            "repo_full_name": repo_full_name,
            "branch": branch,
            "commit": after_commit,
            "github_event": x_github_event,
            "github_delivery_id": x_github_delivery,
            "timestamp": datetime.utcnow().isoformat(),
            "triggered_by": "github-webhook"
        }

        # Publish to Kafka
        try:
            producer = get_kafka_producer()
            future = producer.send(
                KAFKA_TOPIC,
                key=repo_name.encode('utf-8'),
                value=deployment_event
            )
            # Wait for send to complete (with timeout)
            record_metadata = future.get(timeout=10)

            logger.info(f"Published deployment event to Kafka")
            logger.info(f"  Topic: {record_metadata.topic}")
            logger.info(f"  Partition: {record_metadata.partition}")
            logger.info(f"  Offset: {record_metadata.offset}")

            return {
                "status": "queued",
                "repo": repo_name,
                "branch": branch,
                "commit": after_commit[:7],
                "kafka_topic": record_metadata.topic,
                "kafka_partition": record_metadata.partition,
                "kafka_offset": record_metadata.offset
            }

        except Exception as e:
            logger.error(f"Failed to publish to Kafka: {e}")
            raise HTTPException(status_code=500, detail=f"Kafka error: {str(e)}")

    elif x_github_event == 'release':
        # Handle release events (future enhancement)
        logger.info(f"Release event received (not yet implemented)")
        return {"status": "ignored", "reason": "Release events not yet implemented"}

    elif x_github_event == 'ping':
        # GitHub sends ping when webhook is first configured
        logger.info("Received ping event (webhook configured successfully)")
        return {"status": "pong", "message": "Webhook receiver operational"}

    else:
        # Ignore other event types
        logger.info(f"Ignoring event type: {x_github_event}")
        return {"status": "ignored", "reason": f"Event type not handled: {x_github_event}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

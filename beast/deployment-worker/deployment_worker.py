#!/usr/bin/env python3
"""
Beast Deployment Worker
Consumes deployment events from Kafka and executes git pull + docker compose
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, Optional

from kafka import KafkaConsumer, KafkaProducer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/home/jimmyb/deployment-worker.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration from environment
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_INPUT_TOPIC = os.getenv('KAFKA_INPUT_TOPIC', 'deployment-webhooks')
KAFKA_OUTPUT_TOPIC = os.getenv('KAFKA_OUTPUT_TOPIC', 'deployment-results')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'deployment-worker')

# Repository deployment configurations
REPO_CONFIGS = {
    'mundus-editor-application': {
        'path': '/home/jimmyb/Mundus-editor-application',
        'compose_path': '/home/jimmyb/Mundus-editor-application',
        'compose_file': 'docker-compose.yml',
        'enabled': True
    },
    'Mundus-editor-application': {
        'path': '/home/jimmyb/Mundus-editor-application',
        'compose_path': '/home/jimmyb/Mundus-editor-application',
        'compose_file': 'docker-compose.yml',
        'enabled': True
    },
    'dev-rag': {
        'path': '/home/jimmyb/dev-rag',
        'compose_path': None,  # No docker compose yet
        'enabled': False  # Not yet implemented
    },
    'dev-network': {
        'path': '/home/jimmyb/dev-network',
        'compose_path': '/home/jimmyb/dev-network/beast/docker',
        'compose_file': 'docker-compose.yml',
        'enabled': True
    },
    'network-infrastructure': {
        'path': '/home/jimmyb/dev-network',
        'compose_path': '/home/jimmyb/dev-network/beast/docker',
        'compose_file': 'docker-compose.yml',
        'enabled': True
    }
}


def execute_command(command: str, cwd: Optional[str] = None, timeout: int = 300) -> Dict:
    """
    Execute shell command and return result

    Args:
        command: Command to execute
        cwd: Working directory
        timeout: Timeout in seconds (default 5 minutes)

    Returns:
        Dict with success, stdout, stderr, returncode
    """
    logger.info(f"Executing: {command}")
    if cwd:
        logger.info(f"Working directory: {cwd}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout} seconds")
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'returncode': -1
        }
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }


def deploy_repo(repo_name: str, commit: str, branch: str) -> Dict:
    """
    Deploy a repository by pulling latest code and restarting services

    Args:
        repo_name: Repository name
        commit: Commit hash
        branch: Branch name

    Returns:
        Dict with success, message, details
    """
    logger.info(f"Starting deployment for {repo_name} (commit: {commit[:7]}, branch: {branch})")

    # Get repo configuration
    config = REPO_CONFIGS.get(repo_name)
    if not config:
        logger.warning(f"No configuration found for repository: {repo_name}")
        return {
            'success': False,
            'message': f'Repository {repo_name} not configured for deployment',
            'details': {}
        }

    if not config.get('enabled', False):
        logger.warning(f"Deployment disabled for repository: {repo_name}")
        return {
            'success': False,
            'message': f'Deployment disabled for {repo_name}',
            'details': {}
        }

    repo_path = config['path']
    compose_path = config.get('compose_path')
    compose_file = config.get('compose_file', 'docker-compose.yml')

    deployment_log = []

    # Step 1: Git pull
    logger.info(f"Step 1: Pulling latest code from {branch}")
    git_result = execute_command(f'git pull origin {branch}', cwd=repo_path)
    deployment_log.append({
        'step': 'git_pull',
        'command': f'git pull origin {branch}',
        'success': git_result['success'],
        'output': git_result['stdout'],
        'error': git_result['stderr']
    })

    if not git_result['success']:
        logger.error(f"Git pull failed: {git_result['stderr']}")
        return {
            'success': False,
            'message': f'Git pull failed for {repo_name}',
            'details': {
                'log': deployment_log,
                'error': git_result['stderr']
            }
        }

    # Step 2: Docker compose (if configured)
    if compose_path:
        logger.info(f"Step 2: Restarting Docker services")

        # Build and restart
        compose_cmd = f'docker compose -f {compose_file} up -d --build'
        compose_result = execute_command(compose_cmd, cwd=compose_path, timeout=600)
        deployment_log.append({
            'step': 'docker_compose',
            'command': compose_cmd,
            'success': compose_result['success'],
            'output': compose_result['stdout'],
            'error': compose_result['stderr']
        })

        if not compose_result['success']:
            logger.error(f"Docker compose failed: {compose_result['stderr']}")
            return {
                'success': False,
                'message': f'Docker compose failed for {repo_name}',
                'details': {
                    'log': deployment_log,
                    'error': compose_result['stderr']
                }
            }
    else:
        logger.info(f"Step 2: No Docker compose configured, skipping")
        deployment_log.append({
            'step': 'docker_compose',
            'command': None,
            'success': True,
            'output': 'No Docker compose configured',
            'error': ''
        })

    # Success!
    logger.info(f"Deployment successful for {repo_name}")
    return {
        'success': True,
        'message': f'Successfully deployed {repo_name} (commit: {commit[:7]})',
        'details': {
            'log': deployment_log,
            'commit': commit,
            'branch': branch
        }
    }


def publish_result(producer: KafkaProducer, deployment_event: Dict, result: Dict):
    """
    Publish deployment result to Kafka

    Args:
        producer: Kafka producer
        deployment_event: Original deployment event
        result: Deployment result
    """
    result_event = {
        'event_type': 'deployment_result',
        'repo_name': deployment_event.get('repo_name'),
        'repo_full_name': deployment_event.get('repo_full_name'),
        'branch': deployment_event.get('branch'),
        'commit': deployment_event.get('commit'),
        'github_delivery_id': deployment_event.get('github_delivery_id'),
        'original_timestamp': deployment_event.get('timestamp'),
        'result_timestamp': datetime.utcnow().isoformat(),
        'success': result['success'],
        'message': result['message'],
        'details': result.get('details', {})
    }

    try:
        future = producer.send(
            KAFKA_OUTPUT_TOPIC,
            key=deployment_event.get('repo_name', '').encode('utf-8'),
            value=result_event
        )
        record_metadata = future.get(timeout=10)

        logger.info(f"Published deployment result to Kafka")
        logger.info(f"  Topic: {record_metadata.topic}")
        logger.info(f"  Partition: {record_metadata.partition}")
        logger.info(f"  Offset: {record_metadata.offset}")
    except Exception as e:
        logger.error(f"Failed to publish result to Kafka: {e}")


def main():
    """Main worker loop"""
    logger.info("=" * 80)
    logger.info("Beast Deployment Worker Starting")
    logger.info("=" * 80)
    logger.info(f"Kafka bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}")
    logger.info(f"Input topic: {KAFKA_INPUT_TOPIC}")
    logger.info(f"Output topic: {KAFKA_OUTPUT_TOPIC}")
    logger.info(f"Consumer group: {KAFKA_GROUP_ID}")
    logger.info("=" * 80)

    # Initialize Kafka consumer
    logger.info("Connecting to Kafka...")
    consumer = KafkaConsumer(
        KAFKA_INPUT_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',  # Start from latest (not beginning)
        enable_auto_commit=True,
        auto_commit_interval_ms=1000
    )

    # Initialize Kafka producer (for results)
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',
        retries=3
    )

    logger.info("Connected to Kafka successfully!")
    logger.info("Waiting for deployment events...")
    logger.info("=" * 80)

    # Main consumer loop
    try:
        for message in consumer:
            deployment_event = message.value

            logger.info("=" * 80)
            logger.info("Received deployment event!")
            logger.info(f"  Repository: {deployment_event.get('repo_full_name')}")
            logger.info(f"  Branch: {deployment_event.get('branch')}")
            logger.info(f"  Commit: {deployment_event.get('commit', '')[:7]}")
            logger.info(f"  Triggered by: {deployment_event.get('triggered_by')}")
            logger.info(f"  Kafka partition: {message.partition}")
            logger.info(f"  Kafka offset: {message.offset}")
            logger.info("=" * 80)

            # Execute deployment
            repo_name = deployment_event.get('repo_name')
            commit = deployment_event.get('commit', '')
            branch = deployment_event.get('branch', 'main')

            result = deploy_repo(repo_name, commit, branch)

            # Publish result
            publish_result(producer, deployment_event, result)

            # Log result
            if result['success']:
                logger.info("✅ Deployment SUCCESSFUL")
            else:
                logger.error("❌ Deployment FAILED")
                logger.error(f"   Error: {result['message']}")

            logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)
    finally:
        logger.info("Closing Kafka connections...")
        consumer.close()
        producer.close()
        logger.info("Deployment worker stopped")


if __name__ == "__main__":
    main()

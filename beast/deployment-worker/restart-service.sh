#!/bin/bash
# Restart deployment-worker service
# Run this after updating deployment_worker.py configuration

set -e

echo "Restarting deployment-worker service..."
sudo systemctl restart deployment-worker.service

echo "Waiting for service to start..."
sleep 2

echo ""
echo "Service status:"
sudo systemctl status deployment-worker.service --no-pager

echo ""
echo "Recent logs (last 20 lines):"
sudo journalctl -u deployment-worker.service --no-pager -n 20

echo ""
echo "✅ Service restarted successfully!"

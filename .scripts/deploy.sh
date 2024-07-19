#!/bin/bash
set -e
echo "Deployment started ..."

git pull origin dev

echo "restart tasks ..."
sudo systemctl restart celery

echo "restart scanmycodes ..."
sudo systemctl restart scanmycodes

echo "Deployment finished!"

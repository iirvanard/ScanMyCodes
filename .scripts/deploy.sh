#!/bin/bash
set -e
echo "Deployment started ..."

git pull origin dev

sudo systemctl restart celery

sudo systemctl restart scanmycodes

echo "Deployment finished!"

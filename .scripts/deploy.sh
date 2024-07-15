#!/bin/bash
set -e

echo "Deployment started ..."

git pull origin dev

docker compose -f ./production.yml build --no-cache

docker compose -f ./production.yml up -d

echo "Deployment finished!"
#!/bin/bash
set -e

echo "Deployment started ..."

git pull origin dev

docker compose build 

docker compose up -d

echo "Deployment finished!"
#!/bin/bash
set -e

echo "Deployment started ..."

git pull origin dev

docker compose -f ./production.yml build

docker compose -f ./production.yml up 

echo "Deployment finished!"
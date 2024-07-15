#!/bin/bash
set -e

echo "Deployment started ..."

docker compose -f ./production.yml build

docker compose -f ./production.yml up

echo "Deployment finished!"
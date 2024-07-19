#!/bin/bash
set -e
echo "Deployment started ..."

git pull origin dev

# for docker
# docker compose build 

# docker compose up -d


# native flask

# restarting the celery 

sudo pkill -9 -f 'celery worker'

source source tugas_akhir/venv/bin/activate

celery -A app:celery worker --loglevel=info --detach

sudo systemctl restart scanmycodes


# echo "Deployment finished!"

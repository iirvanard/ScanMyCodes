#!/bin/bash
set -e
echo "Deployment started ..."

git pull origin dev

# for docker
# docker compose build 

# docker compose up -d


# native flask

# restarting the celery 

# Memeriksa apakah ada proses Celery worker yang berjalan
if pgrep -f 'celery worker' > /dev/null; then
    echo "Celery worker ditemukan. Menghentikan proses yang ada..."
    sudo pkill -9 -f 'celery worker'
else
    echo "Tidak ada Celery worker yang berjalan."
fi

# Mengaktifkan virtual environment
source venv/bin/activate

# Menjalankan Celery worker
echo "Menjalankan Celery worker..."
celery -A app:celery worker --loglevel=info 
sudo systemctl restart scanmycodes


echo "Deployment finished!"

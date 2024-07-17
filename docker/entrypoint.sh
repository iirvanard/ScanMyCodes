#!/bin/bash

export $(grep -v '^#' .env | xargs)



if [ ! -d "migrations" ]; then
  flask db init
fi
flask db migrate -m 'create initial tables'
flask db upgrade

if [ "$FLASK_ENV" = "production" ]; then
  gunicorn run:app --bind=0.0.0.0:5000 --timeout 120 --workers=3 --threads=3 --worker-connections=1000
else 
  flask run --debug
fi



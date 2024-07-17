#!/bin/bash

export $(grep -v '^#' .env | xargs)



if [ ! -d "migrations" ]; then
  flask db init
fi
flask db migrate -m 'create initial tables'
flask db upgrade

if [ "$FLASK_ENV" = "production" ]; then
  gunicorn --bind=0.0.0.0 --timeout 600 run:app
else 
  flask run --debug
fi



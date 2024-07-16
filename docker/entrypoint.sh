#!/bin/bash

if [ ! -f .env ]
then
  export $(cat .env | xargs)
fi


if [ ! -d "migrations" ]; then
  flask db init
fi
flask db migrate -m 'create initial tables'
flask db upgrade


if [ "$FLASK_ENV" = "production" ]; then
  gunicorn run:app -b 0.0.0.0:5000
else
  flask run --debug
fi

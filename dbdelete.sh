#!/bin/bash
set -e
rm -rf migrations/
flask db init
flask db migrate 
flask db upgrade
#!/bin/sh
set -e

# entrar na pasta do app se o WORKDIR não for /app
cd /app

python manage.py migrate --noinput
python manage.py load_initial_fixtures

python manage.py runserver 0.0.0.0:8000

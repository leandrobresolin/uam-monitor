#!/bin/sh
set -e

cd /app

python manage.py migrate --noinput
python manage.py load_initial_fixtures

# Roda API em background + simulator
python manage.py runserver 0.0.0.0:8000 &
python manage.py run_flight_simulator

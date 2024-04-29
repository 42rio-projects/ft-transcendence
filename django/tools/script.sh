#!/bin/sh

echo > ~/.pg_service.conf "[admin]
host=$POSTGRES_HOST
port=$POSTGRES_PORT
dbname=$POSTGRES_NAME
user=$POSTGRES_USER
password=$POSTGRES_PASSWORD"

echo "MakeMigrations"
python manage.py makemigrations
echo "Migrate"
python manage.py migrate --run-syncdb
echo "Runserver"
gunicorn ft_transcendence.wsgi:application --bind 0.0.0.0:8000 --access-logfile '-' --error-logfile '-' --log-level INFO
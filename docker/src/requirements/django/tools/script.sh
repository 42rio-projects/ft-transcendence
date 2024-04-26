#!/bin/sh

echo > ~/.pg_service.conf "[admin]
host=$POSTGRES_HOST
port=$POSTGRES_PORT
dbname=$POSTGRES_NAME
user=$POSTGRES_USER
password=$POSTGRES_PASSWORD"

python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

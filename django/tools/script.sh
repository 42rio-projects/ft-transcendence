#!/bin/sh

echo > ~/.pg_service.conf "[admin]
host=$POSTGRES_HOST
port=$POSTGRES_PORT
dbname=$POSTGRES_NAME
user=$POSTGRES_USER
password=$POSTGRES_PASSWORD"

# Check if the Gunicorn config file exists
if [ ! -f gunicorn_config.py ]; then
    # Create Gunicorn config file with default settings
    cat << EOF > gunicorn_config.py
bind = '0.0.0.0:8000'
workers = 3
accesslog = '-'
errorlog = '-'
loglevel = 'info'
EOF
fi

echo "Gunicorn config updated!"


echo "MakeMigrations"
python manage.py makemigrations

echo "Migrate"
python manage.py migrate --run-syncdb

echo "Initialize database"
python manage.py init_db

echo "CollectStatic"
python manage.py collectstatic --noinput

echo "CreateSuperUser"
python manage.py createsuperuser --noinput

echo "Runserver"
gunicorn -c gunicorn_config.py ft_transcendence.wsgi:application

#!/bin/sh
echo ""
cat /opt/application/webapp/RELEASE
echo "------------------------------------------------"
echo "DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}"
echo "DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}"
echo "DJANGO_BIND_HOST=${DJANGO_BIND_HOST}"
echo "------------------------------------------------"
echo "Waiting for database ${MYSQL_USER}@${MYSQL_HOST}:${MYSQL_PORT}..."
while ! nc -z ${MYSQL_HOST} ${MYSQL_PORT}; do
  sleep 0.1
done
echo "Database ok"
echo "Collect static files..."
python manage.py collectstatic --no-input --clear --settings=base.settings.docker
ls -al /opt/application/webapp/staticfiles
echo "Migrate database..."
python manage.py migrate
gunicorn project.asgi:application --worker-class=uvicorn.workers.UvicornWorker --bind ${DJANGO_BIND_HOST} --workers=3 --worker-tmp-dir /dev/shm

#!/bin/bash
set -e

echo "Starting Classic Models API..."

# Display version information
echo "API Version: $(python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development'); import django; django.setup(); from config.settings.base import get_version; print(get_version())")"

# Use MYSQL_HOST environment variable, default to 'mysql' for local development
MYSQL_HOST=${MYSQL_HOST:-mysql}

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready at ${MYSQL_HOST}..."
until nc -z "${MYSQL_HOST}" 3306; do
  echo "MySQL is unavailable - sleeping"
  sleep 2
done

echo "MySQL is up - proceeding with migrations"

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --noinput

# Create demo user if it doesn't exist
echo "Creating demo user if it doesn't exist..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='demo').exists():
    User.objects.create_user('demo', 'demo@example.com', 'demo123')
    print('Demo user created')
else:
    print('Demo user already exists')
"

# Start the Django development server
echo "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000

#!/bin/bash
set -e

echo "Starting Classic Models API..."

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
until nc -z mysql 3306; do
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

#!/bin/bash
set -e

echo "Initializing Classic Models database..."

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
until mysql -h mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword} -e "SELECT 1" > /dev/null 2>&1; do
  echo "MySQL is unavailable - sleeping"
  sleep 2
done

echo "MySQL is ready - initializing database"

# Check if the database exists and has tables
TABLE_COUNT=$(mysql -h mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword} -e "USE classicmodels; SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'classicmodels';" 2>/dev/null | tail -1)

if [ "$TABLE_COUNT" -gt 0 ]; then
  echo "Database already initialized with $TABLE_COUNT tables"
else
  echo "Initializing database with sample data..."
  
  # Execute the SQL file
  mysql -h mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword} classicmodels < /docker-entrypoint-initdb.d/01-init.sql
  
  # Verify tables were created
  TABLE_COUNT=$(mysql -h mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword} -e "USE classicmodels; SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'classicmodels';" 2>/dev/null | tail -1)
  echo "Database initialized with $TABLE_COUNT tables"
fi

echo "Database initialization complete"
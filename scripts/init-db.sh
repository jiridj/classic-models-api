#!/bin/bash

# Script to initialize the Classic Models database
# This script will be run inside the MySQL container during initialization

echo "Initializing Classic Models database..."

# Wait for MySQL to be ready
until mysqladmin ping -h localhost -u root -prootpassword --silent; do
    echo "Waiting for MySQL to be ready..."
    sleep 2
done

echo "MySQL is ready. Database initialization completed."
echo "Classic Models database is now available with sample data."

#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "==================================="
echo "Waiting for PostgreSQL to start..."
echo "==================================="

# Wait for PostgreSQL to be ready
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done

echo "PostgreSQL started successfully!"

echo "==================================="
echo "Running database migrations..."
echo "==================================="
python manage.py migrate --no-input

echo "==================================="
echo "Collecting static files..."
echo "==================================="
python manage.py collectstatic --no-input --clear

echo "==================================="
echo "Starting Django application..."
echo "==================================="

# Execute the main command (passed as arguments)
exec "$@"
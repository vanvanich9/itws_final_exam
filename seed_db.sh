#!/bin/sh
set -e

DATABASE_HOST="${DATABASE_HOST:-postgres}"
DATABASE_PORT="${DATABASE_PORT:-5432}"
DATABASE_USERNAME="${DATABASE_USERNAME:-postgres}"
DATABASE_PASSWORD="${DATABASE_PASSWORD:-postgres}"
DATABASE_NAME="${DATABASE_NAME:-db}"

export PGPASSWORD="$DATABASE_PASSWORD"

echo "Checking database for existing records..."

until psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USERNAME" -d "$DATABASE_NAME" -c '\q' 2>/dev/null; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

TABLE_EXISTS=$(psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USERNAME" -d "$DATABASE_NAME" -tAc \
  "SELECT EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'users'
  )")

if [ "$TABLE_EXISTS" = "t" ]; then
  USER_COUNT=$(psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USERNAME" -d "$DATABASE_NAME" -tAc \
    'SELECT COUNT(*) FROM users')
else
  USER_COUNT=0
fi

if [ "$USER_COUNT" -gt 0 ]; then
  echo "Database already has ${USER_COUNT} user(s), skipping seed dump."
  exit 0
fi

if [ ! -f /db_dump.sql ]; then
  echo "Dump file not found: /db_dump.sql" >&2
  exit 1
fi

echo "Database is empty, applying dump from /db_dump.sql..."
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USERNAME" -d "$DATABASE_NAME" -v ON_ERROR_STOP=1 -f /db_dump.sql
echo "Seed dump applied successfully."

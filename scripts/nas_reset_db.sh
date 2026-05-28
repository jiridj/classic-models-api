#!/usr/bin/env bash
set -euo pipefail

# Resets the MySQL database on the NAS deployment by removing the persistent
# mysql_data volume and recreating the stack.
#
# WARNING: This irreversibly deletes all MySQL data for this compose project.
#
# Usage:
#   ./scripts/nas_reset_db.sh
#
# Optional:
#   COMPOSE_FILE=docker-compose.yml ./scripts/nas_reset_db.sh

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

echo "Resetting MySQL volume using compose file: $COMPOSE_FILE"
echo "WARNING: This will delete the persistent MySQL volume (all data)."
echo "Stopping stack and removing volumes..."
docker compose -f "$COMPOSE_FILE" down -v

echo "Starting stack..."
docker compose -f "$COMPOSE_FILE" up -d

echo "Done. The MySQL container will re-initialize from ./db/mysqlsampledatabase.sql"

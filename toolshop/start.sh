#!/usr/bin/env bash
# Start a private Toolshop in Docker, load fresh seed data, wait until UI and API answer.
#   bash toolshop/start.sh                          -> PROD  (UI :4200, API :8091)
#   SPRINT=sprint5-with-bugs bash toolshop/start.sh -> BUGGY (hash routing: ROUTE_PREFIX=/#)
# Stop and wipe:  docker compose -f toolshop/docker-compose.yml down
set -euo pipefail
cd "$(dirname "$0")"
export SPRINT="${SPRINT:-sprint5}"
dc() { docker compose -f docker-compose.yml "$@"; }

dc up -d

echo "Waiting for the database..."
for _ in $(seq 1 60); do
  dc exec -T mariadb mysqladmin ping -h localhost -u root -proot --silent 2>/dev/null && break
  sleep 2
done

echo "Loading seed data ($SPRINT)..."
dc exec -T laravel-api php artisan migrate:fresh --seed --force > /dev/null

echo "Waiting for the API..."
curl -fsS --retry 30 --retry-delay 2 --retry-all-errors http://localhost:8091/status
echo

echo "Waiting for the UI (Angular compiles on first start, about 1-2 minutes)..."
for _ in $(seq 1 120); do
  if [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:4200 || true)" = 200 ]; then
    echo "Toolshop $SPRINT is ready: UI http://localhost:4200, API http://localhost:8091"
    exit 0
  fi
  sleep 5
done
dc logs --tail 50 angular-ui
echo "The UI did not start within 10 minutes." >&2
exit 1

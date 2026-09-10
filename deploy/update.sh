#!/usr/bin/env bash
set -Eeuo pipefail

# Run from the deployed project directory as the application user.
APP_DIR="${APP_DIR:-/home/perfumeapp/perfume_labels_system}"
SERVICE_NAME="${SERVICE_NAME:-perfume_labels_system}"

cd "$APP_DIR"
mkdir -p backups

# Keep a dated copy before every deployment. The database is intentionally not
# in Git; this is what preserves production data across git pulls.
if [[ -f db.sqlite3 ]]; then
    cp -p db.sqlite3 "backups/db-$(date +%Y%m%d-%H%M%S).sqlite3"
fi

git pull --ff-only
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
deactivate
sudo systemctl restart "$SERVICE_NAME"

echo "Deployment complete. Database backups are in $APP_DIR/backups/"

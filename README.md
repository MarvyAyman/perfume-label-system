# Perfume Label System — Django project

A ready-to-run Django project for perfume label printing. It includes migrations, login, search, printing endpoints, Arabic/English/German translations, session persistence, and reporting.

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open **http://127.0.0.1:8000/**. The default language is German; `/ar/`, `/en/`, and `/de/` are available.

## Production deployment

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for the complete GitHub-to-Contabo VPS setup using Gunicorn, Nginx, systemd, HTTPS, and SQLite backups. The `deploy/` directory contains the systemd service, Nginx configuration, environment template, and safe update script.

## Database and redeploys

The production database is `db.sqlite3`. It is deliberately excluded from Git, along with `.env`, virtual environments, static build output, and backups. Keep the production database on the VPS and back it up before updates. Redeploy by running `bash deploy/update.sh` inside the existing clone; do not delete and reclone the directory.

If the current local database already contains your products and users, copy it to the VPS once during initial setup with `scp db.sqlite3 ...` before running `python manage.py migrate`.

## Everyday use

- **Products & batches** — add perfumes, add EZLOT batches, mark one active per perfume, and disable a perfume without losing its history.
- **Ingredients** — maintain current ingredients text per perfume.
- **Reports & records** — search permanent tracking-label history and export it to CSV.
- **Printing** — browser printing supports separate tracking and ingredient label workflows.

The Zebra ZD411 printers remain connected to the computer or till doing the physical printing. The VPS hosts the web application; it does not need direct access to the printers.

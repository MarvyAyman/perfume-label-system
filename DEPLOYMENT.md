# Deploying to a Contabo VPS with GitHub, Gunicorn, Nginx, and SQLite

This project is designed for a normal Ubuntu VPS. **SQLite is persistent on the VPS filesystem, but it is intentionally excluded from Git.** A redeploy must update the existing directory in place; it must not delete and reclone the directory, because that would remove the production database.

The examples use:

- Linux user: `perfumeapp`
- Application directory: `/home/perfumeapp/perfume_labels_system`
- Systemd service: `perfume_labels_system`
- Repository: replace `YOUR_GITHUB_REPO_URL` with your GitHub URL

## 1. Push the project to GitHub

Run these commands locally from the project directory. Do not add `db.sqlite3`, `.env`, or `venv/` to Git.

```bash
git init
git add .
git status                         # review this before committing
git commit -m "Initial Django application"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

If `db.sqlite3` was already tracked before the new `.gitignore`, remove it from Git's index without deleting your local file:

```bash
git rm --cached db.sqlite3
git commit -m "Keep production SQLite database out of Git"
git push
```

## 2. Prepare the VPS as root

Log in using the Contabo root IP and password, then create a dedicated application user. Use SSH keys afterward and disable password login when you are comfortable doing so.

```bash
ssh root@YOUR_VPS_IP
apt update && apt upgrade -y
apt install -y git python3-venv python3-pip nginx
adduser perfumeapp
usermod -aG sudo perfumeapp
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
exit
```

From this point, use the application user:

```bash
ssh perfumeapp@YOUR_VPS_IP
```

## 3. Clone and install the application

```bash
cd /home/perfumeapp
git clone YOUR_GITHUB_REPO_URL perfume_labels_system
cd /home/perfumeapp/perfume_labels_system
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp deploy/.env.example .env
chmod 600 .env
nano .env
```

Set at least:

```dotenv
DJANGO_SECRET_KEY=GENERATE_A_UNIQUE_LONG_SECRET
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=YOUR_VPS_IP
DJANGO_CSRF_TRUSTED_ORIGINS=
DJANGO_HTTPS=False
```

Generate a secret with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 4. Initialize the database and static files

The first deployment creates a new empty SQLite file. If you need to deploy the existing local `db.sqlite3` with its current products/users/data, copy it to the VPS **once** before running migrations, using a secure method such as `scp`:

```bash
# Run on your local computer, from the project directory:
scp db.sqlite3 perfumeapp@YOUR_VPS_IP:/home/perfumeapp/perfume_labels_system/db.sqlite3
```

Then on the VPS:

```bash
cd /home/perfumeapp/perfume_labels_system
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
# Only if the copied database does not already contain an account:
python manage.py createsuperuser
deactivate
```

**Do not run `makemigrations` on every deployment.** Create and commit migrations only when models change; deploy those committed migration files with the code and run `migrate` on the VPS.

## 5. Install Gunicorn as a systemd service

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/perfume_labels_system.service
sudo systemctl daemon-reload
sudo systemctl enable --now perfume_labels_system
sudo systemctl status perfume_labels_system
```

The service file uses the same application path and loads the private `.env` file. Check logs if it does not start:

```bash
sudo journalctl -u perfume_labels_system -n 100 --no-pager
```

## 6. Configure Nginx

```bash
sudo cp deploy/nginx_perfume_system.conf /etc/nginx/sites-available/perfume_labels_system
sudo ln -s /etc/nginx/sites-available/perfume_labels_system /etc/nginx/sites-enabled/perfume_labels_system
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

Before running `nginx -t`, edit `server_name` in the copied file to your domain or VPS IP. The site should then be reachable at `http://YOUR_VPS_IP/`.

## 7. HTTPS after a domain is connected

Point the domain's DNS A record to the VPS, then run:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

After HTTPS is working, update `.env`:

```dotenv
DJANGO_ALLOWED_HOSTS=your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
DJANGO_HTTPS=True
```

Then restart:

```bash
sudo systemctl restart perfume_labels_system
```

## 8. Safe redeployment after a GitHub change

Never delete the application directory and never run `git clone` again over it. The update script creates a timestamped SQLite backup, pulls the committed code, runs migrations, collects static files, and restarts Gunicorn:

```bash
cd /home/perfumeapp/perfume_labels_system
bash deploy/update.sh
```

If your service or directory differs, override them for that run:

```bash
APP_DIR=/home/perfumeapp/perfume_labels_system SERVICE_NAME=perfume_labels_system bash deploy/update.sh
```

The database remains at `/home/perfumeapp/perfume_labels_system/db.sqlite3`. Git never overwrites it because it is ignored and remains an untracked local file.

## 9. Backups

The update script keeps a backup before every deployment in `backups/`. Also create an off-server backup schedule; a backup on the same VPS does not protect against VPS loss:

```bash
mkdir -p /home/perfumeapp/backups
crontab -e
```

For a simple local VPS copy, add:

```cron
0 3 * * * cp -p /home/perfumeapp/perfume_labels_system/db.sqlite3 /home/perfumeapp/backups/db-$(date +\%F).sqlite3
```

Periodically download or copy those backups to another machine. SQLite is suitable for this small single-shop application; move to PostgreSQL if multiple users will write heavily at the same time.

## Important SQLite rule

GitHub stores **code and migrations**, not live application data. The production `db.sqlite3` belongs only on the VPS and in backups. A redeploy should be `git pull --ff-only`, `migrate`, `collectstatic`, and service restart—not delete, reclone, or restore an old database from Git.

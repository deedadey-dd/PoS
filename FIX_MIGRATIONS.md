# Fix: No Migrations Detected

## Problem
When you run `python manage.py makemigrations`, it says "No changes detected" because the apps don't have `migrations` directories yet.

## Solution

Run these commands in your terminal (with venv activated):

```bash
# Create migrations directories for all apps
mkdir -p core/migrations
touch core/migrations/__init__.py

mkdir -p inventory/migrations
touch inventory/migrations/__init__.py

mkdir -p transfers/migrations
touch transfers/migrations/__init__.py

mkdir -p sales/migrations
touch sales/migrations/__init__.py

mkdir -p accounting/migrations
touch accounting/migrations/__init__.py

mkdir -p notifications/migrations
touch notifications/migrations/__init__.py

mkdir -p analytics/migrations
touch analytics/migrations/__init__.py

mkdir -p config/migrations
touch config/migrations/__init__.py
```

Or use this one-liner:
```bash
for app in core inventory transfers sales accounting notifications analytics config; do mkdir -p $app/migrations && touch $app/migrations/__init__.py; done
```

Then run:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```


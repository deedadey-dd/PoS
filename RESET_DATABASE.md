# Reset Database - Migration History Issue

## Problem
The error `InconsistentMigrationHistory` occurs because:
- Django's built-in migrations (admin, auth) were already applied
- But we're using a custom User model (`core.User`)
- Django's admin depends on the User model, but the core migrations don't exist yet

## Solution: Fresh Start

Since this is development with no data, we'll delete the database and start fresh:

```bash
# 1. Delete the database
rm db.sqlite3  # Git Bash
# or
del db.sqlite3  # Windows CMD

# 2. Delete migration files (except __init__.py)
# This is optional - you can keep them if you want

# 3. Create fresh migrations
python manage.py makemigrations

# 4. Apply migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser
```

## Alternative: Keep Existing Database

If you have data you want to keep, you can fake the initial migration:

```bash
python manage.py migrate core 0001 --fake
python manage.py migrate
```

But for a fresh project, deleting the database is the cleanest solution.


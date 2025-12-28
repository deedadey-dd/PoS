# Quick Start Guide

## Important: Always Activate Virtual Environment First!

Before running any Django commands, you **must** activate the virtual environment.

### For Git Bash / MINGW64:
```bash
source .venv/Scripts/activate
```

You should see `(.venv)` at the start of your prompt.

### For PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

### For Command Prompt:
```cmd
.venv\Scripts\activate.bat
```

## Complete Setup Steps

1. **Activate virtual environment:**
   ```bash
   source .venv/Scripts/activate  # Git Bash
   ```

2. **Create migrations (if you've modified models):**
   ```bash
   python manage.py makemigrations
   ```

3. **Run migrations (create database tables):**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## Verify Virtual Environment is Active

After activating, check:
```bash
which python  # Should show .venv/Scripts/python
# or
python --version  # Should show Python 3.11.3
```

If you see the system Python path instead of `.venv`, the activation didn't work.


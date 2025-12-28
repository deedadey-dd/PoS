# Activating Virtual Environment

## Git Bash / MINGW64 (Your Current Terminal)

```bash
source .venv/Scripts/activate
```

After activation, you should see `(.venv)` at the start of your prompt.

Then install dependencies:
```bash
pip install -r requirements.txt
```

## Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

## Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

## Verify Activation

After activating, verify Django is available:
```bash
python -c "import django; print(django.get_version())"
```

## Quick Setup Steps

1. Activate virtual environment (see above for your terminal type)
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Install dependencies: `pip install -r requirements.txt`
4. Create migrations: `python manage.py makemigrations`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`

import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_system.settings')
django.setup()

from core.models import User

def update_password():
    print("Updating admin password...")
    try:
        user = User.objects.get(username='admin')
        user.set_password('Gifted12345')
        user.save()
        print("Password updated successfully for user 'admin'.")
    except User.DoesNotExist:
        print("User 'admin' does not exist.")
    except Exception as e:
        print(f"Error updating password: {e}")

if __name__ == '__main__':
    update_password()

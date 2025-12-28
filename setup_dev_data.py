import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_system.settings')
django.setup()

from core.models import Tenant, Location, Role, User, UserLocationRole, LocationType

def setup_data():
    print("Setting up development data...")

    # 1. Create Tenant
    tenant, created = Tenant.objects.get_or_create(
        name='Default Tenant',
        defaults={
            'slug': 'default',
            'domain': 'localhost',
            'currency': 'USD'
        }
    )
    print(f"Tenant: {tenant.name} (Created: {created})")

    # 2. Create Location
    location, created = Location.objects.get_or_create(
        code='MAIN',
        tenant=tenant,
        defaults={
            'name': 'Main Store',
            'location_type': LocationType.STORE
        }
    )
    print(f"Location: {location.name} (Created: {created})")

    # 3. Create Role
    role, created = Role.objects.get_or_create(
        code='admin',
        tenant=tenant,
        defaults={
            'name': 'Administrator',
            'description': 'Full access'
        }
    )
    print(f"Role: {role.name} (Created: {created})")

    # 4. Create User
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password',
            tenant=tenant
        )
        print("User: admin created")
    else:
        user = User.objects.get(username='admin')
        print("User: admin already exists")

    # 5. Assign Role
    ulr, created = UserLocationRole.objects.get_or_create(
        user=user,
        location=location,
        role=role
    )
    print(f"Role assigned: {created}")

    print("Done!")

if __name__ == '__main__':
    setup_data()

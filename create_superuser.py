import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogapp_api.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import DatabaseError

def create_superuser():
    try:
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'Admin@123')
            print('Superuser created successfully!')
        else:
            print('Superuser already exists.')
    except DatabaseError as e:
        print(f'Database error: {e}')
    except Exception as e:
        print(f'Error creating superuser: {e}')

if __name__ == '__main__':
    create_superuser()
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz_project.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    try:
        admin_user = User.objects.get(email="admin@gmail.com")
        print("Admin user already exists")
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            username="admin",
            email="admin@gmail.com",
            password="Admin@123"
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("Admin user created successfully")

if __name__ == "__main__":
    create_admin_user()
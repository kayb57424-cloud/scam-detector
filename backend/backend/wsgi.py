"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()

# AUTO-CREATE SUPERUSER (only when CREATE_ADMIN=1)
if os.environ.get("CREATE_ADMIN") == "1":
    try:
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")
        if username and password and not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email or "", password=password)
            print(f"Superuser {username} created.")
    except Exception as exc:
        print("Auto-create superuser failed:", exc)

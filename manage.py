#!/usr/bin/env python
import os
import sys
import subprocess
import atexit
import django

def start_docker_compose():
    print("🚀 Starting all docker-compose services...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    print("✅ All services started.")

def stop_docker_compose():
    print("🛑 Stopping all docker-compose services...")
    try:
        subprocess.run(["docker", "compose", "stop"], check=True)
        print("✅ All services stopped.")
    except subprocess.CalledProcessError:
        print("⚠️ Failed to stop services.")

def init_superuser():
    from django.contrib.auth import get_user_model
    user = get_user_model()

    admin_username = os.environ.get("DJANGO_ADMIN_USERNAME", "admin")
    admin_email = os.environ.get("DJANGO_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("DJANGO_ADMIN_PASSWORD", "admin123")

    if not user.objects.filter(username=admin_username).exists():
        user.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        print(f"✅ Superuser '{admin_username}' created successfully!")
    else:
        print(f"ℹ️ Superuser '{admin_username}' already exists.")

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    DEBUG = os.environ.get("DEBUG", "True").lower() in ["1", "true", "yes"]
    runserver_related = len(sys.argv) > 1 and sys.argv[1] in ["runserver", "migrate", "shell"]

    if runserver_related and DEBUG:
        if os.environ.get("RUN_MAIN") or sys.argv[1] != "runserver":
            start_docker_compose()
            atexit.register(stop_docker_compose)

    try:
        from django.core.management import execute_from_command_line, call_command
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if len(sys.argv) > 1 and sys.argv[1] == "runserver" and os.environ.get("RUN_MAIN"):
        print("💾 Setting up Django...")
        django.setup()
        print("💾 Applying migrations automatically...")
        call_command("migrate", interactive=False)
        init_superuser()

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
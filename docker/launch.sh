#!/bin/bash

# Migrate if no changes has been made or migration is allowed
needMigration="$(python manage.py makemigrations)"
hasMigration="$(python manage.py showmigrations | awk -e '/\[ \]/ { print $0 }')"
if [[ $MAGE_ALLOW_MIGRATIONS = True || ($needMigration = "No changes detected" && $hasMigration = "") ]]; then
  python manage.py migrate;
  python manage.py collectstatic --noinput;
  python manage.py synccheckers;
else
  echo "Database migration can't be done";
  exit 1;
fi

if [[ "$DJANGO_ROOT_INITIAL_PASSWORD" != "" ]]; then
  python3 manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os
User = get_user_model()
if not User.objects.filter(username="root").exists():
    User.objects.create_superuser("root", "root@mage.local", os.getenv("DJANGO_ROOT_INITIAL_PASSWORD"))
EOF
fi

gunicorn --workers=2 --bind=0.0.0.0:8000 --access-logfile=- --error-logfile=- --log-level=INFO --forwarded-allow-ips=* MAGE.wsgi

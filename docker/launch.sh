#!/bin/bash

# Migrate if no changes has been made or migration is allowed
needMigration="$(python manage.py makemigrations)"
hasMigration="$(python manage.py showmigrations | awk -e '/\[ \]/ { print $0 }')"
if [[ $MAGE_ALLOW_MIGRATIONS = True || ($needMigration = "No changes detected" && $hasMigration = "") ]]; then
  python manage.py migrate;
  python manage.py collectstatic --noinput;
  python manage.py createsuperuser;
  python manage.py synccheckers;
else
  echo "Database migration can't be done";
  exit 1;
fi

/usr/sbin/httpd -D FOREGROUND -e info
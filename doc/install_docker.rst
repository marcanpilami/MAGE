Installation with Docker
##########################

Prerequisites
*************

* OS: a recent Linux
* Docker daemon or equivalent
* Optionally, a database (Oracle >= 10g, PostgresQL, mysql). Default is sqlite 3 - it is bundled with Python, so nothing special is required. In other databases, you will
  need an account with the permission to create tables, sequences and indexes (or their equivalent in your database).

  * Obviously the database can also run inside Docker, but this is your choice.


MAGE itself
***********

Just run: ::

    docker run -it -e "DJANGO_ROOT_INITIAL_PASSWORD=something" -e "MAGE_CREATE_DEMO_DATA=True" -e "MAGE_ALLOW_MIGRATIONS=True" -p 8000:8000 enioka/mage:nightly

Other available image tags are `latest` or specific version tags. Full list available on Docker Hub.

Configuration can be done through environment variables:

* database properties

  * DATABASE_ENGINE: either nothing (sqlite3) or a specific driver (`django.db.backends.postgresql_psycopg2` for postresql, `django.db.backends.mysql` for MySQL).
  * DATABASE_NAME
  * DATABASE_HOST
  * DATABASE_PORT
  * DATABASE_USER
  * DATABASE_PASSWORD

* security properties:

  * DJANGO_ALLOWED_HOSTS: a comma-separated list of HTTP hostnames allowed to query MAGE. Very useful behind a reverse proxy. Wildcard is also possible.
  * DJANGO_SECRET_KEY: set it to a unique random string. Used for some signature purposes.
  * DJANGO_ROOT_INITIAL_PASSWORD: if set, a user named `root` is created with this password if it does not exist yet.

This image contains drivers for sqlite, postgresql and sqlite3. Using this image as a base image, it is possible to create MAGE images with other drivers in custom images.

If you are using sqlite for the database, note the directory `/code/deployment/db` is a volume and contains the database file.

The image listens on port 8000.

The image runs database migrations on startup if needed if `MAGE_ALLOW_MIGRATIONS` is set to `True`.

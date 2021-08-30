FROM python:3.8-alpine

ENV APP_NAME=MAGE \
    WORKDIR=/var/www/MAGE \
    APP_DIR=/var/www/MAGE \
    DATABASE_ENGINE="" \
    DATABASE_NAME="" \
    DATABASE_HOST="" \
    DATABASE_PORT="" \
    DATABASE_USER="" \
    DATABASE_PASSWORD="" \
    ALLOWED_HOSTS="localhost" \
    DEBUG=""  \
    INTERNAL_IPS="" \
    SECRET_KEY="your_own_here" \
    AZURE_ACCOUNT_NAME="" \
    AZURE_ACCOUNT_KEY="" \
    AZURE_CONTAINER="" \
    MAGE_ALLOW_MIGRATIONS=True

RUN apk update
RUN apk add apache2 apache2-dev gcc libc-dev linux-headers apache2-mod-wsgi

# Create working dir
WORKDIR $WORKDIR

RUN sed -i 's/Listen 80/# Listen 80/' /etc/apache2/httpd.conf

RUN chown apache:apache /var/www/*
USER apache

ENV VIRTUAL_ENV=$WORKDIR/mage-venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Collect and install requirements
COPY requirements.txt $WORKDIR
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --upgrade
# db modules support
RUN pip install psycopg2 mysqlclient cx_Oracle

COPY --chown=apache docker/mage_httpd.conf /etc/apache2/conf.d/

#COPY . .
COPY --chown=apache . .

RUN python manage.py collectstatic --noinput
# inject environment parameters or users parameters
RUN python manage.py createsuperuser
RUN python manage.py synccheckers

VOLUME $WORKDIR/tmp/media

EXPOSE 8000
#USER root
RUN chmod 755 ./docker/launch.sh
CMD ./docker/launch.sh
#CMD python manage.py runmodwsgi --port=8000 --user apache --group apache --server-root=/etc/apache2/ --rewrite-rules /etc/apache2/mage_httpd.conf
#CMD mod_wsgi-express start-server $WORKDIR/$APP_NAME/wsgi.py --port=8000 --user apache --group apache
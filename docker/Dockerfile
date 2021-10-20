FROM python:3.9

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

# Collect and install necessary packages
RUN apt-get update
RUN apt-get -y install apache2 apache2-dev gcc libc-dev make

# Collect mod_wsgi last version and build it against installed python version
WORKDIR /tmp
RUN wget -q "https://github.com/GrahamDumpleton/mod_wsgi/archive/refs/tags/4.9.0.tar.gz"
RUN tar -xzf '4.9.0.tar.gz'
RUN cd ./mod_wsgi-4.9.0
RUN ls -al
WORKDIR /tmp/mod_wsgi-4.9.0
RUN ./configure --with-python=/usr/local/bin/python3.9 --with-apxs=/usr/bin/apxs
RUN make
RUN make install
# Enable mod_wsgi apache load
RUN echo "LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" > /etc/apache2/mods-enabled/wsgi_module.load
# clean
RUN rm /tmp/4.9.0.tar.gz && rm -R /tmp/mod_wsgi-4.9.0

# Create working dir
WORKDIR $WORKDIR

# Port 80 can't be used as apache user
RUN sed -i 's/Listen 80/# Listen 80/' /etc/apache2/ports.conf

RUN chown -R www-data:www-data /var/www
RUN chown -R www-data:www-data /var/log/apache2
RUN mkdir /var/run/apache2
RUN chown -R www-data:www-data /var/run/apache2

# Collect and install requirements
COPY requirements.txt $WORKDIR
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --upgrade
# db modules support
RUN pip install psycopg2 mysqlclient cx_Oracle

# Install mage apache conf
COPY --chown=www-data docker/mage_httpd.conf /etc/apache2/conf-enabled/

# Copy mage
COPY --chown=www-data . .

VOLUME $WORKDIR/tmp/media

EXPOSE 8000

USER www-data
RUN chmod 755 ./docker/launch.sh
CMD ./docker/launch.sh
FROM python:3.8-alpine

ENV APP_NAME=MAGE
ENV WORKDIR=/home/$APP_NAME
# TODO: create a python function to handle empty values
#    DATABASE_ENGINE="" \
#    DATABASE_NAME="" DATABASE_HOST="" DATABASE_PORT="" DATABASE_USER="" DATABASE_PASSWORD="" \
#    ALLOWED_HOSTS="" INTERNAL_IPS="" \
#    MEDIA_ROOT="" MEDIA_URL="" STATIC_ROOT="" STATIC_URL="" \
#    SECRET_KEY="your_own_here" AZURE_ACCOUNT_NAME="" AZURE_ACCOUNT_KEY="" AZURE_CONTAINER=""

# TODO: Load ODBC drivers postgresql mysql oracle
# RUN apk add postgresql postgresql-contrib
# RUN apk add nginx gcc libc-dev linux-headers
RUN apk update
RUN apk add apache2 apache2-dev gcc libc-dev linux-headers

RUN addgroup -S $APP_NAME && adduser -S $APP_NAME -G $APP_NAME


# Create working dir
WORKDIR $WORKDIR

# Collect and install requirements
COPY requirements.txt $WORKDIR
RUN pip install -r requirements.txt --upgrade

# RUN pip install <drivers>
RUN pip install mod_wsgi

COPY docker/mage_httpd.conf /etc/apache2/httpd.conf

USER $APP_NAME
COPY --chown=$APP_NAME . .

# Create databases objects
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput
# inject environment parameters or users parameters
RUN python manage.py createsuperuser
RUN python manage.py synccheckers

# RUN python manage.py shell
# from scm.demo_items import create_test_is
# create_test_is()

EXPOSE 8000

CMD mod_wsgi-express start-server $WORKDIR/$APP_NAME/wsgi.py


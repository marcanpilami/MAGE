# FROM nginx:alpine AS webserver
# RUN ls /etc/nginx/

# COPY docker/nginx.conf /etc/nginx/sites-available/
# RUN mkdir -p /etc/nginx/sites-enabled/ && ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/

FROM python:3.8-alpine

ENV APP_NAME=MAGE
ENV WORKDIR=/home/$APP_NAME \
    DATABASE_ENGINE=django.db.backends.sqlite3

# Load ODBC drivers postgresql mysql oracle
# RUN apk add postgresql postgresql-contrib
RUN apk add nginx gcc libc-dev linux-headers
# RUN apk upgrade

RUN addgroup -S $APP_NAME && adduser -S $APP_NAME -G $APP_NAME

# RUN cat /etc/nginx/nginx.conf

RUN mkdir -p /etc/nginx/sites-enabled/
RUN mkdir -p /etc/nginx/sites-available/

COPY ./docker/mage_nginx.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/

# Create working dir
WORKDIR $WORKDIR

# Collect and install requirements
COPY requirements.txt $WORKDIR
RUN pip install -r requirements.txt --upgrade

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

USER root
CMD ["uwsgi", "--ini", "uwsgi.ini"]
CMD ["nginx", "-g", "daemon off;"]
#CMD ["uwsgi", "--http", "0.0.0.0:8000", "--module", "MAGE.wsgi"]
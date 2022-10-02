FROM python:3.10-alpine

LABEL "vendor"="enioka Haute Couture"
LABEL "vendor.url"="https://haute-couture.enioka.com"

# System
RUN apk --no-cache upgrade
RUN apk add --no-cache tree grep sed build-base python3-dev mysql-dev bash

WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE=1, \
    PYTHONUNBUFFERED=1 \
    APP_NAME=MAGE \
    DATABASE_ENGINE= \
    DATABASE_NAME= \
    DATABASE_HOST= \
    DATABASE_PORT= \
    DATABASE_USER= \
    DATABASE_PASSWORD= \
    AZURE_ACCOUNT_NAME= \
    AZURE_ACCOUNT_KEY= \
    AZURE_CONTAINER= \
    MAGE_ALLOW_MIGRATIONS=True \
    DJANGO_ALLOWED_HOSTS=* \
    DJANGO_INTERNAL_IPS="" \
    DJANGO_SECRET_KEY="your_own_here" \
    DJANGO_DEBUG=False \
    DJANGO_ROOT_INITIAL_PASSWORD=

COPY ./requirements.txt /code/
RUN python -m pip install --upgrade pip && pip install psycopg2-binary mysqlclient && pip install gunicorn && pip install whitenoise[brotli] ;
RUN sed -i "/## Following/q;p" requirements.txt && pip install --no-cache-dir --upgrade -r requirements.txt


# Python website install & init
COPY . /code/
COPY ./MAGE/local_settings.docker.py /code/MAGE/local_settings.py

RUN addgroup -g 500 -S django && adduser --system --no-create-home --uid 500 -G django django
RUN python manage.py collectstatic --no-input ;
RUN mkdir -p /code/deployment/media /code/tmp && chown -R django:django /code && chmod -R 400 . && find -type d -exec  chmod 500 {} \; && chmod -R 700 deployment tmp /code/docker/launch.sh

USER django

STOPSIGNAL SIGINT
EXPOSE 8000
VOLUME /code/deployment/media

#RUN ls -alrt /code/docker; false
CMD /code/docker/launch.sh

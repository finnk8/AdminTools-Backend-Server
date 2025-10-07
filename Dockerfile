FROM python:3.13-slim


# Build-Deps für mysqlclient
RUN apk add --no-cache \
      mariadb-connector-c-dev \
      gcc \
      musl-dev \
      python3-dev

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache \
      build-base \
      gfortran \
      musl-dev \
      freetype-dev \
      libpng-dev \
      pkgconfig

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY . .

RUN python manage.py collectstatic --noinput

RUN python manage.py makemigrations --noinput 

# Port für Gunicorn exposed (Standard 8000)
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=server.settings

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Gunicorn starten (Standard-Port 8000, Host 0.0.0.0)
CMD ["gunicorn", "main.wsgi", "--timeout", "300", "--workers", "2"]

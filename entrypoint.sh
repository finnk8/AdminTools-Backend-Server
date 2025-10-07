#!/bin/sh
set -e

# 1) Warte auf Datenbank (falls das nötig ist)
until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Waiting for DB…"
  sleep 1
done

# 2) Migrationen
python manage.py migrate --noinput

# 3) optional: Superuser per ENV anlegen
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
EOF
fi

# 4) Staticfiles
python manage.py collectstatic --noinput

# 5) Start the server
exec "$@"

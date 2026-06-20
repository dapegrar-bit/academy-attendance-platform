web: python manage.py migrate --noinput && python manage.py init_platform && gunicorn academy_platform.wsgi:application --bind 0.0.0.0:$PORT

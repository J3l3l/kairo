web: gunicorn kairo.wsgi:application
worker: celery -A kairo worker -l info
beat: celery -A kairo beat -l info 
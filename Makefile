mr:
	python manage.py makemigrations && python manage.py migrate && python manage.py runserver
r:
	python manage.py runserver
beat:
	#celery -A config beat
	celery -A config beat
	#celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
	#celery -A config worker --loglevel=info
celery:
	celery -A config worker -l INFO
celeryup:
	celery -A config worker -Q warehouse,celery
flower:
	celery -A config flower  --address=127.0.0.1 --port=5566
startup:
	python manage.py migrate
	python manage.py collectstatic --no-input
	daphne -b 0.0.0.0 -p 8000 config.asgi:application
	python manage.py create_products
	python manage.py create_user

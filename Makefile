mr:
	python manage.py makemigrations && python manage.py migrate && python manage.py runserver
r:
	python manage.py runserver
beat:
	#celery -A config beat
	celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
	#celery -A config worker --loglevel=info
celery:
	celery -A config worker -l INFO
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_routes = {
    'fruitshop.tasks.task_joker': {'queue': 'celery'},
    'fruitshop.tasks.task_buy_fruits': {'queue': 'celery'},
    'fruitshop.tasks.task_sell_fruits': {'queue': 'celery'},
    'fruitshop.tasks.task_check_warehouse': {'queue': 'warehouse'}
                        }


app.autodiscover_tasks(['users','fruitshop'])

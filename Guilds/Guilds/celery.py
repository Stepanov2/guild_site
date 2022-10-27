import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Guilds.settings')

app = Celery('Guilds')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_for_emails_to_send': {
        'task': 'guild_site.tasks.send_mass_email',
        'schedule': 60  # crontab(minute='*/2')
    }
}


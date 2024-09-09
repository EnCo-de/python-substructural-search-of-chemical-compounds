from celery import Celery

# Celery configuration
celery = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include=['src.tasks']
)

celery.conf.task_track_started = True
# celery.conf.update(task_track_started=True)
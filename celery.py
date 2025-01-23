from celery import Celery

# Konfigurasi Celery dengan Redis sebagai broker
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['REDIS_URL'],
        broker=app.config['REDIS_URL']
    )
    celery.conf.update(app.config)
    return celery

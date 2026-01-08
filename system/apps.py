from django.apps import AppConfig
from mongoengine import connect
from django.conf import settings

class SystemsigoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'system'

    def ready(self):
        connect(
            db=settings.MONGODB_SETTINGS['db'],
            host=settings.MONGODB_SETTINGS['host']
        )
from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "store"

    # def ready(self):
    #     from . import prints
    #     prints.start()
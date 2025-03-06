from django.apps import AppConfig


class OnlineshopappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'OnlineShopApp'

    def ready(self):
        import OnlineShopApp.signals  # Подключаем сигнал
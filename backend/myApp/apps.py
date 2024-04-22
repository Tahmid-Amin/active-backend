from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myApp'

    def ready(self):
        # Import models to ensure signals defined in models.py are connected and ready
        print("MyApp is ready.")
        import myApp.models
        import myApp.signals
        print("Signal connections should be set.")
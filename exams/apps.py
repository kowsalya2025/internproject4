# exams/apps.py
from django.apps import AppConfig

class ExamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exams'
    
    def ready(self):
        # Import signals here to avoid circular imports
        import exams.signals

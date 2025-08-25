from django.apps import AppConfig

class ResultsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'results'

    def ready(self):
        from results.models import KetQuaXoSo
        from .models import CachTinhDanDe
        try:
            CachTinhDanDe.validate_calculation_methods()
        except ValueError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Validation error: {str(e)}")
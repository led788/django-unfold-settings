from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class PackageSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'unfold_settings'
    verbose_name = _("Application Settings")

    def ready(self):
        try:
            import unfold_settings.signals
        except ImportError:
            pass

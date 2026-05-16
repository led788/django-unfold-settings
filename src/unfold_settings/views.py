from django.db.models.fields.files import FieldFile
from django.http import JsonResponse
from django.views import View


from django.conf import settings
from django.core.cache import cache

from .models import Setting


class SettingsView(View):
    """
    API endpoint returning all configurations as a flat JSON object.
    Optimized with Django Cache API and dynamic TTL config.
    """

    CACHE_KEY = "package_app_settings_data"

    def get(self, request, *args, **kwargs):
        # 1. Attempt to get data from cache
        cached_data = cache.get(self.CACHE_KEY)
        if cached_data is not None:
            return JsonResponse(
                cached_data, safe=False, json_dumps_params={"ensure_ascii": False}
            )

        # 2. If no cache exists, fetch data from DB in exactly 1 SQL query
        settings_queryset = Setting.objects.select_related(
            "string_value",
            "text_value",
            "html_value",
            "bool_value",
            "json_value",
            "date_value",
            "datetime_value",
            "file_value",
        )

        flat_settings = {}
        for setting in settings_queryset:
            raw_value = setting.value

            # Check if the value is a Django FieldFile object
            if isinstance(raw_value, FieldFile):
                # .url returns relative path (e.g., /media/uploads/logo.png)
                flat_settings[setting.key] = raw_value.url if bool(raw_value) else None

            # If it's a string that already contains a file path (handled by model property)
            elif isinstance(raw_value, str) and raw_value.startswith("/media/"):
                flat_settings[setting.key] = raw_value

            # Date check
            elif hasattr(raw_value, "isoformat"):
                flat_settings[setting.key] = raw_value.isoformat()

            # All other types (strings, booleans, JSON)
            else:
                flat_settings[setting.key] = raw_value

        # 3. Read TTL from main project settings.py (default is 3600 seconds / 1 hour)
        # Example setting in project settings.py: APP_SETTINGS_CACHE_TTL = 7200
        DEFAULT_TTL = 3600

        # 2. Get raw value from main project settings.py
        raw_ttl = getattr(settings, "APP_SETTINGS_CACHE_TTL", DEFAULT_TTL)

        # 3. Validate data type and correctness
        # Check if value is an integer AND NOT a boolean (since True/False are int subclasses in Python)
        if isinstance(raw_ttl, int) and not isinstance(raw_ttl, bool):
            # If negative value provided, force to 0 (disable cache)
            cache_ttl = max(0, raw_ttl)
        else:
            # If string, None, list, float or bool provided, rollback to default
            cache_ttl = DEFAULT_TTL

        if cache_ttl:
            cache.set(self.CACHE_KEY, flat_settings, timeout=cache_ttl)

        return JsonResponse(
            flat_settings, safe=False, json_dumps_params={"ensure_ascii": False}
        )

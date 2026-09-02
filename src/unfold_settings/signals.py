from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from unfold_settings.models import (
    Setting,
    StringValue,
    TextValue,
    HTMLValue,
    IntegerValue,
    FloatValue,
    BoolValue,
    JSONValue,
    DateValue,
    DateTimeValue,
    FileValue,
)

# Define the cache key to be cleared
CACHE_KEY = "package_app_settings_data"


@receiver([post_save, post_delete], sender=Setting)
def clear_settings_cache_on_parent_change(sender, instance, **kwargs):
    """Resets cache when the base Setting model is modified or deleted."""
    cache.delete(CACHE_KEY)


@receiver([post_save, post_delete], sender=StringValue)
@receiver([post_save, post_delete], sender=TextValue)
@receiver([post_save, post_delete], sender=HTMLValue)
@receiver([post_save, post_delete], sender=IntegerValue)
@receiver([post_save, post_delete], sender=FloatValue)
@receiver([post_save, post_delete], sender=BoolValue)
@receiver([post_save, post_delete], sender=JSONValue)
@receiver([post_save, post_delete], sender=DateValue)
@receiver([post_save, post_delete], sender=DateTimeValue)
@receiver([post_save, post_delete], sender=FileValue)
def clear_settings_cache_on_value_change(sender, instance, **kwargs):
    """Resets cache when any related value inline is modified or deleted."""
    cache.delete(CACHE_KEY)

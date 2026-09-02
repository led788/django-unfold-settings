import os

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def settings_upload_path(instance, filename):
    """Generates upload path for files: uploads/settings/<key>/<filename>"""
    return os.path.join("uploads", "settings", instance.setting.key, filename)


class Setting(models.Model):
    """
    Base configuration model. Stores unique key and general description.
    Actual typed values are linked via precise OneToOne relations.
    """

    key = models.CharField(
        _("Key"),
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_("Unique configuration key used by the frontend."),
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Detailed description of what this setting controls."),
    )

    class Meta:
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")
        ordering = ["key"]

    def __str__(self):
        return self.key

    # Strict list of reverse relations mapping to the exact related_name attributes
    VALUE_RELATIONS = [
        "string_value",
        "text_value",
        "html_value",
        "int_value",
        "float_value",
        "bool_value",
        "json_value",
        "date_value",
        "datetime_value",
        "file_value",
    ]

    @staticmethod
    def _relation_is_empty(relation, related_obj):
        """
        True when a value row physically exists but carries no real data.
        Lets a stale row (e.g. a blanked string left behind when switching
        the setting to another type) stop counting as an occupied type.
        """
        raw = related_obj.value
        if relation == "file_value":
            return not bool(raw)
        if relation == "bool_value":
            # False is a meaningful value, never "empty".
            return False
        if relation == "json_value":
            return raw in (None, {}, [], "")
        return raw is None or raw == ""

    @property
    def value(self):
        """
        Safely looks for the filled value.
        Catches DoesNotExist if the OneToOne relation is missing in the DB.
        """
        for relation in self.VALUE_RELATIONS:
            try:
                related_obj = getattr(self, relation, None)
                if related_obj is not None and not self._relation_is_empty(
                    relation, related_obj
                ):
                    return related_obj.value
            except models.ObjectDoesNotExist:
                # If the OneToOne relation is not created in the DB, Django will throw this exception.
                # We skip it and look in the next table.
                continue
        return None

    def clean(self):
        """Database-level integrity validation preventing cross-type pollution."""
        super().clean()

        # Skip model-level validation if we are in the context of saving
        # through Django Admin. BaseSettingValueFormSet already performed
        # the necessary validation, and at this stage, linked inlines are not yet
        # removed from the DB, which leads to false positives and 500 errors.
        if hasattr(self, "_filled_types_tracker"):
            return

        filled_relations = []
        for relation in self.VALUE_RELATIONS:
            try:
                related_obj = getattr(self, relation, None)
                if related_obj is not None and not self._relation_is_empty(
                    relation, related_obj
                ):
                    filled_relations.append(relation)
            except models.ObjectDoesNotExist:
                continue

        if len(filled_relations) > 1:
            type_names = [r.replace("_value", "").upper() for r in filled_relations]
            raise ValidationError(
                _(
                    "A setting cannot have multiple data types simultaneously. You filled: %(types)s"
                ),
                code="multiple_types_forbidden",
                params={"types": ", ".join(type_names)},
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# Explicit OneToOne relations defined in child classes to guarantee naming consistency
class StringValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="string_value"
    )
    value = models.CharField(_("Value"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("String Value")
        verbose_name_plural = _("String Values")


class TextValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="text_value"
    )
    value = models.TextField(_("Value"), blank=True)

    class Meta:
        verbose_name = _("Text Value")
        verbose_name_plural = _("Text Values")


class HTMLValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="html_value"
    )
    value = models.TextField(_("HTML Code"), blank=True)

    class Meta:
        verbose_name = _("HTML Value")
        verbose_name_plural = _("HTML Values")


class IntegerValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="int_value"
    )
    value = models.BigIntegerField(_("Integer"), null=True, blank=True)

    class Meta:
        verbose_name = _("Integer Value")
        verbose_name_plural = _("Integer Values")


class FloatValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="float_value"
    )
    value = models.FloatField(_("Float"), null=True, blank=True)

    class Meta:
        verbose_name = _("Float Value")
        verbose_name_plural = _("Float Values")


class BoolValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="bool_value"
    )
    value = models.BooleanField(_("Enabled"), default=False)

    class Meta:
        verbose_name = _("Boolean Value")
        verbose_name_plural = _("Boolean Values")


class JSONValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="json_value"
    )
    value = models.JSONField(_("JSON Data"), default=dict, blank=True)

    class Meta:
        verbose_name = _("JSON Value")
        verbose_name_plural = _("JSON Values")


class DateValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="date_value"
    )
    value = models.DateField(_("Date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Date Value")
        verbose_name_plural = _("Date Values")


class DateTimeValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="datetime_value"
    )
    value = models.DateTimeField(_("Date and Time"), null=True, blank=True)

    class Meta:
        verbose_name = _("Date Time Value")
        verbose_name_plural = _("Date Time Values")


class FileValue(models.Model):
    setting = models.OneToOneField(
        Setting, on_delete=models.CASCADE, related_name="file_value"
    )
    value = models.FileField(_("File"), upload_to=settings_upload_path)

    class Meta:
        verbose_name = _("File Value")
        verbose_name_plural = _("File Values")

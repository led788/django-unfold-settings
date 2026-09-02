
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
from unfold.admin import ModelAdmin, TabularInline
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import admin


class BaseSettingValueFormSet(forms.BaseInlineFormSet):
    """
    Formset validator that checks cleaned data across all inlines.
    Eliminates false positives for empty JSON, Bool, and File fields.
    """

    def clean(self):
        super().clean()

        # We need to collect filled types from ALL inlines on the current page.
        # Since clean() is called for each inline separately, we store the
        # state in the parent form object (form.instance) to avoid duplicate checks.
        if not hasattr(self.instance, "_filled_types_tracker"):
            self.instance._filled_types_tracker = set()

        # Mapping of models to their user-friendly names
        model_names = {
            "StringValue": _("String Value"),
            "TextValue": _("Text Value"),
            "HTMLValue": _("HTML Value"),
            "IntegerValue": _("Integer Value"),
            "FloatValue": _("Float Value"),
            "BoolValue": _("Boolean Value"),
            "JSONValue": _("JSON Data"),
            "DateValue": _("Date Value"),
            "DateTimeValue": _("Date Time Value"),
            "FileValue": _("File Value"),
        }

        # Iterate through forms in the current inline
        for form in self.forms:
            # We are only interested in valid forms that are not marked for deletion
            if (
                form.is_valid()
                and form.cleaned_data
                and not form.cleaned_data.get("DELETE", False)
            ):
                value = form.cleaned_data.get("value")
                model_name = form.instance.__class__.__name__

                # Logic for determining if the field is actually filled
                is_filled = False

                if model_name == "JSONValue":
                    # JSON is considered filled only if it contains data (not an empty dict/list)
                    if value and value != {} and value != []:
                        is_filled = True
                elif model_name == "BoolValue":
                    # For Boolean, we check if the field was touched in the POST request,
                    # as False is also a valid state for the flag.
                    # However, if the object is created from scratch and the flag is just default False,
                    # we don't count it as explicitly filled if other fields are empty.
                    if form.has_changed():
                        is_filled = True
                elif value is not None and value != "":
                    # For all other types (String, Text, HTML, Date, File)
                    is_filled = True

                if is_filled and model_name in model_names:
                    self.instance._filled_types_tracker.add(model_names[model_name])

        # If more than one data type is detected after checking all inlines
        if len(self.instance._filled_types_tracker) > 1:
            # Sort for clean output
            conflict_types = sorted(list(self.instance._filled_types_tracker))
            raise ValidationError(
                _(
                    "Validation Error: You can only fill ONE data type for a setting. "
                    "You currently have data in: %(types)s. Please clear the extra fields."
                ),
                params={"types": ", ".join([str(t) for t in conflict_types])},
            )


# ==========================================
# INLINE BLOCK REGISTRATIONS FOR UNFOLD
# ==========================================


class StringValueInline(TabularInline):
    model = StringValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


class TextValueInline(TabularInline):
    model = TextValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


class HTMLValueInline(TabularInline):
    model = HTMLValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


class IntegerValueInline(TabularInline):
    model = IntegerValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


class FloatValueInline(TabularInline):
    model = FloatValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


class BoolValueInline(TabularInline):
    model = BoolValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


class JSONValueInline(TabularInline):
    model = JSONValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


class DateValueInline(TabularInline):
    model = DateValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


class DateTimeValueInline(TabularInline):
    model = DateTimeValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


class FileValueInline(TabularInline):
    model = FileValue
    fields = ["value"]
    max_num = 1
    formset = BaseSettingValueFormSet


# ==========================================
# MAIN DASHBOARD INTERFACE CONFIGURATION
# ==========================================


@admin.register(Setting)
class SettingAdmin(ModelAdmin):
    list_display = ["key", "description", "get_type", "display_value"]
    search_fields = ["key", "description"]

    inlines = [
        StringValueInline,
        TextValueInline,
        HTMLValueInline,
        IntegerValueInline,
        FloatValueInline,
        BoolValueInline,
        JSONValueInline,
        DateValueInline,
        DateTimeValueInline,
        FileValueInline,
    ]

    def get_queryset(self, request):
        """Optimizes queries via select_related to fix N+1 performance bottleneck."""
        qs = super().get_queryset(request)
        return qs.select_related(*Setting.VALUE_RELATIONS)

    @admin.display(description=_("Data Type"))
    def get_type(self, obj):
        """Safely identifies active relation block and updates dashboard listing column status."""
        for relation in Setting.VALUE_RELATIONS:
            try:
                related_obj = getattr(obj, relation, None)
                if related_obj is not None and not Setting._relation_is_empty(
                    relation, related_obj
                ):
                    return relation.replace("_value", "").upper()
            except ObjectDoesNotExist:
                continue
        return _("NOT SET")

    @admin.display(description=_("Current Value"))
    def display_value(self, obj):
        val = obj.value
        if val is None:
            return "-"
        if hasattr(val, "name") and not isinstance(val, (str, bytes)):
            return val.name.split("/")[-1]
        str_val = str(val)
        return f"{str_val[:47]}..." if len(str_val) > 50 else str_val

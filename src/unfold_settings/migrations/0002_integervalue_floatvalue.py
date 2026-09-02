# Generated for numeric setting value types.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("unfold_settings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="IntegerValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.BigIntegerField(blank=True, null=True, verbose_name="Integer")),
                ("setting", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="int_value", to="unfold_settings.setting")),
            ],
            options={
                "verbose_name": "Integer Value",
                "verbose_name_plural": "Integer Values",
            },
        ),
        migrations.CreateModel(
            name="FloatValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.FloatField(blank=True, null=True, verbose_name="Float")),
                ("setting", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="float_value", to="unfold_settings.setting")),
            ],
            options={
                "verbose_name": "Float Value",
                "verbose_name_plural": "Float Values",
            },
        ),
    ]

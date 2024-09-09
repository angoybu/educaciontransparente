# Generated by Django 4.2.15 on 2024-09-04 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_resource"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="resource",
            options={"verbose_name": "recurso", "verbose_name_plural": "recursos"},
        ),
        migrations.AddField(
            model_name="resource",
            name="url",
            field=models.URLField(blank=True, default="", verbose_name="url"),
        ),
    ]

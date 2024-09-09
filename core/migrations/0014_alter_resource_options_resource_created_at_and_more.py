# Generated by Django 4.2.15 on 2024-09-07 15:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_alter_resource_document_alter_resource_url"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="resource",
            options={
                "ordering": ("updated_at", "name"),
                "verbose_name": "recurso",
                "verbose_name_plural": "recursos",
            },
        ),
        migrations.AddField(
            model_name="resource",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="creado_el",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="resource",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado_el"),
        ),
    ]

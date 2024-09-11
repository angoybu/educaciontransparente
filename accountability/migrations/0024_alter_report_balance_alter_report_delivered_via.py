# Generated by Django 4.2.16 on 2024-09-11 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accountability", "0023_receipt_disbursement_receipt_institution_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="balance",
            field=models.IntegerField(editable=False, null=True, verbose_name="saldo"),
        ),
        migrations.AlterField(
            model_name="report",
            name="delivered_via",
            field=models.CharField(
                help_text="Ej. Recibido por RUE, Mesa de entrada",
                max_length=250,
                verbose_name="recepción",
            ),
        ),
    ]

# Generated by Django 4.2.15 on 2024-09-04 04:11

from django.db import migrations, models
import django.db.models.deletion


def add_payment_types(apps, schema_editor):
    PaymentType = apps.get_model("accountability", "PaymentType")
    for name in ("Transferencia", "Cheque", "Depósito"):
        PaymentType.objects.create(name=name)


class Migration(migrations.Migration):
    dependencies = [
        ("accountability", "0012_auto_20240904_0001"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250, verbose_name="nombre")),
            ],
            options={
                "verbose_name": "tipo de pago",
                "verbose_name_plural": "tipos de pago",
            },
        ),
        migrations.AlterField(
            model_name="disbursement",
            name="funds_origin",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="disbursements",
                to="accountability.disbursementorigin",
                verbose_name="origen del fondo",
            ),
        ),
        migrations.AlterField(
            model_name="disbursement",
            name="origin_details",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="disbursements",
                to="accountability.origindetail",
                verbose_name="marco",
            ),
        ),
        migrations.RemoveField(
            model_name="disbursement",
            name="payment_type",
        ),
        migrations.AddField(
            model_name="disbursement",
            name="payment_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="accountability.paymenttype",
                verbose_name="tipo de pago",
            ),
        ),
        migrations.RunPython(add_payment_types, migrations.RunPython.noop),
    ]

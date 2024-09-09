import uuid
from datetime import timedelta

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify


class Resolution(models.Model):
    document_number = models.PositiveIntegerField(
        verbose_name="nro. resolución", null=True
    )
    document_year = models.PositiveIntegerField(
        verbose_name="año de resolución", null=True
    )
    document = models.FileField(
        upload_to="resolutions",
        verbose_name="documento de resolución",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "resolución"
        verbose_name_plural = "resoluciones"

    def __str__(self):
        return f"{self.document_number or ''}/{self.document_year or ''}"


class DisbursementOrigin(models.Model):
    code = models.IntegerField(verbose_name="código")

    class Meta:
        verbose_name = "origen del ingreso"
        verbose_name_plural = "orígenes del ingreso"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code}"


class OriginDetail(models.Model):
    name = models.CharField(verbose_name="nombre", max_length=250)

    class Meta:
        verbose_name = "marco"
        verbose_name_plural = "marcos"

    def __str__(self):
        return self.name


class PaymentType(models.Model):
    name = models.CharField(verbose_name="nombre", max_length=250)

    class Meta:
        verbose_name = "tipo de pago"
        verbose_name_plural = "tipos de pago"

    def __str__(self):
        return self.name


class Disbursement(models.Model):
    resolution = models.ForeignKey(
        Resolution,
        on_delete=models.PROTECT,
        related_name="disbursements",
        verbose_name="resolución",
    )
    institution = models.ForeignKey(
        "core.Institution",
        on_delete=models.CASCADE,
        related_name="disbursements",
        verbose_name="institución",
    )
    disbursement_date = models.DateField(verbose_name="fecha de desembolso", null=True)
    resolution_amount = models.PositiveIntegerField(
        verbose_name="Monto resolución", null=True
    )
    amount_disbursed = models.IntegerField(verbose_name="monto desembolsado", null=True)
    funds_origin = models.ForeignKey(
        DisbursementOrigin,
        on_delete=models.PROTECT,
        related_name="disbursements",
        null=True,
        verbose_name="origen del fondo",
    )
    origin_details = models.ForeignKey(
        OriginDetail,
        on_delete=models.PROTECT,
        related_name="disbursements",
        null=True,
        verbose_name="marco",
    )
    due_date = models.DateField(verbose_name="fecha a rendir", null=True)
    principal_name = models.CharField(
        max_length=200,
        default="",
        blank=True,
        verbose_name="nombre del director",
    )
    principal_issued_id = models.CharField(
        max_length=20, default="", blank=True, verbose_name="C.I. del director"
    )
    payment_type = models.ForeignKey(
        PaymentType, on_delete=models.PROTECT, null=True, verbose_name="tipo de pago"
    )
    documents = GenericRelation(
        "core.Document", related_name="disbursement", verbose_name="documentos"
    )
    pictures = GenericRelation(
        "core.Picture", related_name="expense_report", verbose_name="imágenes"
    )
    comments = models.TextField(default="", blank=True, verbose_name="observaciones")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "desembolso"
        verbose_name_plural = "desembolsos"

    def __str__(self):
        try:
            return f"Des. resol. {self.resolution} ({self.disbursement_date.strftime('%d/%m/%Y')}): {self.institution.name}"
        except:
            return f"Desembolso {self.id}: {self.institution.name}"

    def clean(self):
        if not self.due_date:
            self.due_date = self.disbursement_date + timedelta(days=105)


class Report(models.Model):
    class ReportStatus(models.TextChoices):
        finished = "cancelado", "Cancelado"
        pending = "pendente", "Pendente"

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="actualizado el")
    disbursement = models.OneToOneField(
        Disbursement,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="desembolso",
    )
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.pending,
        editable=False,
    )
    reported_amount = models.PositiveIntegerField(
        verbose_name="monto rendido", null=True, editable=False
    )
    report_date = models.DateField(
        verbose_name="fecha de rendición", editable=False, null=True
    )
    balance = models.IntegerField(verbose_name="saldo", null=True)
    delivered_via = models.CharField(max_length=250, verbose_name="recepción")
    comments = models.TextField(default="", blank=True, verbose_name="observaciones")
    documents = GenericRelation(
        "core.Document", related_name="report", verbose_name="documentos"
    )

    class Meta:
        verbose_name = "rendición"
        verbose_name_plural = "rendiciones"

    def __str__(self):
        try:
            disbursement = self.disbursement.disbursement_date.strftime("%d/%m/%Y")
            due_date = self.disbursement.due_date.strftime("%d/%m/%Y")
        except:
            return f"Rendición {self.id} - Des {self.disbursement_id}"
        return f"Rend. s/ des. {disbursement} (venc. {due_date})"


class ReceiptType(models.Model):
    name = models.CharField("nombre", max_length=100, unique=True)

    class Meta:
        verbose_name = "tipo de comprobante"
        verbose_name_plural = "tipos de comprobante"

    def __str__(self):
        return self.name


class AccountObject(models.Model):
    key = models.PositiveSmallIntegerField(verbose_name="código")
    value = models.CharField(max_length=250, verbose_name="nombre")
    parent = models.ForeignKey(
        "accountability.AccountObject",
        on_delete=models.CASCADE,
        verbose_name="categoría",
        related_name="children",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "objeto"
        verbose_name_plural = "objetos"

    def __str__(self):
        return f"{self.key}: {self.value}"


class ReceiptManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            total=models.Sum(
                models.ExpressionWrapper(
                    models.F("items__unit_price") * models.F("items__quantity"),
                    output_field=models.FloatField(),
                )
            )
        )


class Receipt(models.Model):
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="receipts",
        verbose_name="rendición",
    )
    receipt_type = models.ForeignKey(
        ReceiptType,
        on_delete=models.CASCADE,
        related_name="receipts",
        verbose_name="tipo de comprobante",
    )
    receipt_date = models.DateField(verbose_name="fecha", null=True)
    receipt_number = models.CharField(
        verbose_name="número de comprobante", max_length=30
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    document = models.FileField(
        upload_to="receipts", verbose_name="documento", null=True, blank=True
    )

    objects = ReceiptManager()

    class Meta:
        verbose_name = "comprobante"
        verbose_name_plural = "comprobantes"

    def __str__(self):
        return f"{self.receipt_type} nro. {self.receipt_number}"


class ReceiptItemManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                subtotal=models.ExpressionWrapper(
                    models.F("unit_price") * models.F("quantity"),
                    output_field=models.FloatField(),
                )
            )
        )


class ReceiptItem(models.Model):
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        verbose_name="comprobante",
        related_name="items",
    )
    object_of_expenditure = models.ForeignKey(
        AccountObject,
        on_delete=models.PROTECT,
        verbose_name="objeto de gasto",
        related_name="receipt_items",
        null=True,
    )
    description = models.CharField(max_length=500, verbose_name="concepto")
    unit_price = models.IntegerField(verbose_name="precio unitario")
    quantity = models.FloatField(verbose_name="cantidad", default=1)

    objects = ReceiptItemManager()

    class Meta:
        verbose_name = "detalle"
        verbose_name_plural = "detalles"

    def __str__(self):
        return f"{self.quantity} {self.description}: {self.unit_price * self.quantity}"

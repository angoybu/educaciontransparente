from django.db.models import Sum, ExpressionWrapper, F, Value
from django.db.models.functions import Coalesce
from django.db.models import IntegerField
from django_filters import rest_framework as filters

from rest_framework import viewsets
from rest_framework.response import Response

from accountability.models import (
    Report,
    Disbursement,
    Receipt,
    ReceiptItem,
    AccountObject,
)
from accountability.serializers import (
    ReportSerializer,
    DisbursementSerializer,
    ReceiptSerializer,
    AccountObjectChartSerializer,
    ReceiptItemSerializer,
)
from core.models import Institution


class ReportFilter(filters.FilterSet):
    institution = filters.ModelChoiceFilter(
        queryset=Institution.objects.filter(reports__isnull=False).distinct(),
        label="Institución",
    )

    year = filters.NumberFilter(
        field_name="disbursement__disbursement_date__year", label="Año"
    )

    class Meta:
        model = Report
        fields = ["institution"]


class DisbursementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Disbursement.objects.all()
    serializer_class = DisbursementSerializer


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filterset_class = ReportFilter

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        total_disbursed = (
            Disbursement.objects.filter(reports__in=qs)
            .distinct()
            .aggregate(total=Sum("amount_disbursed"))["total"]
        )
        reported_qs = qs.annotate(
            total_reported=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("receipts__items__unit_price")
                        * F("receipts__items__quantity"),
                        output_field=IntegerField(),
                    )
                ),
                Value(0, output_field=IntegerField()),
            )
        )
        total_reported = reported_qs.aggregate(
            reported=Sum("total_reported", distinct=True)
        )["reported"]
        response_data = super().list(request, *args, **kwargs).data
        response_data["summary"] = {
            "total_disbursed": total_disbursed,
            "total_reported": total_reported,
        }
        return Response(data=response_data)


class ReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer


class ReceiptItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReceiptItem.objects.all()
    serializer_class = ReceiptItemSerializer


class AccountObjectChartViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccountObject.objects.all()
    serializer_class = AccountObjectChartSerializer

    def _get_institution(self):
        institution_id = self.request.GET.get("institution")
        try:
            institution_id = int(institution_id)
        except (ValueError, TypeError):
            return None
        try:
            return Institution.objects.get(pk=institution_id)
        except Institution.DoesNotExist:
            return None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["year"] = self._get_year()
        context["institution"] = self._get_institution()
        return context

    def _get_year(self):
        year = self.request.GET.get("year", None)
        try:
            return int(year)
        except (ValueError, TypeError):
            return None

    def get_queryset(self):
        institution = self._get_institution()
        year = self._get_year()
        if not institution or ("year" in self.request.GET.keys() and not year):
            return AccountObject.objects.none()
        leaf_qs = AccountObject.objects.filter(
            receipt_items__receipt__institution=institution
        )
        if year:
            leaf_qs = leaf_qs.filter(receipt_items__receipt__receipt_date__year=year)
        second_level_qs = AccountObject.objects.filter(
            children__in=leaf_qs.distinct()
        ).distinct()
        top_level_qs = AccountObject.objects.filter(
            children__in=second_level_qs
        ).distinct()
        return top_level_qs

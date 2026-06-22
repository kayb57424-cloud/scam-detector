from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "phone_number",
        "phone_country",
        "source_type",
        "result",
        "reporter_region",
        "created_at"
    )

    search_fields = (
        "phone_number",
        "message",
        "reporter_region"
    )

    list_filter = (
        "result",
        "source_type",
        "reporter_region",
        "phone_country"
    )

    ordering = ("-created_at",)
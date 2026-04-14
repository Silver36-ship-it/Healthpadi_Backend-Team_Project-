from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'facility',
        'procedure',
        'advertised_price',
        'charged_price',
        'status',
        'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['procedure', 'user__username', 'facility__facility_name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

from django.contrib import admin
from reports.models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'report_type', 'status', 'submitted_at', 'assigned_reviewer')
    list_filter = ('status', 'report_type')
    search_fields = ('title', 'author_name', 'keywords')
    ordering = ('-submitted_at',)

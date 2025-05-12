from django.contrib import admin
from .models import DashboardSetting, SavedReport, Notification


@admin.register(DashboardSetting)
class DashboardSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'show_participants_chart', 'show_activities_chart', 'show_materials_chart', 'default_time_range')
    list_filter = ('show_participants_chart', 'show_activities_chart', 'show_materials_chart', 'default_time_range')
    search_fields = ('user__username', 'user__email')
    list_editable = ['show_participants_chart', 'show_activities_chart', 'show_materials_chart', 'default_time_range']


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'report_type', 'is_favorite', 'created_at')
    list_filter = ('report_type', 'is_favorite', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    date_hierarchy = 'created_at'
    list_editable = ['is_favorite']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'is_global', 'user', 'is_read', 'created_at')
    list_filter = ('level', 'is_global', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    list_editable = ['is_read']
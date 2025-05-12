from django.db import models
from core.models import TimestampMixin

class DashboardSetting(TimestampMixin):
    """Model for storing dashboard settings for each user"""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='dashboard_settings')
    
    # Chart display preferences
    show_participants_chart = models.BooleanField(default=True)
    show_activities_chart = models.BooleanField(default=True)
    show_materials_chart = models.BooleanField(default=True)
    
    # Time range preferences
    DEFAULT_RANGES = (
        ('day', 'Aujourd\'hui'),
        ('week', 'Cette semaine'),
        ('month', 'Ce mois'),
        ('year', 'Cette année'),
        ('all', 'Tout'),
    )
    default_time_range = models.CharField(max_length=10, choices=DEFAULT_RANGES, default='week')
    
    # Widget preferences
    widgets_order = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Dashboard settings for {self.user.username}"

class SavedReport(TimestampMixin):
    """Model for saving custom reports"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='saved_reports')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=50)
    parameters = models.JSONField()
    is_favorite = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Notification(TimestampMixin):
    """Model for system notifications displayed on the dashboard"""
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=[
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ], default='info')
    link = models.CharField(max_length=255, blank=True, null=True)
    is_global = models.BooleanField(default=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
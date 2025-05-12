from django.db import models
from django.contrib.auth.models import User

class TimestampMixin(models.Model):
    """Mixin for adding timestamp fields to models"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserProfile(TimestampMixin):
    """Extended user profile with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telephone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.CharField(max_length=255, blank=True, null=True)
    is_staff_member = models.BooleanField(default=False)
    
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('staff', 'Staff Member'),
        ('regular', 'Regular User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='regular')

    def __str__(self):
        return f"{self.user.username}'s Profile"

class AuditLog(models.Model):
    """Model for tracking important changes in the system"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.user} at {self.timestamp}"
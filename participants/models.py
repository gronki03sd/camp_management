from django.db import models
from core.models import TimestampMixin

class Participant(TimestampMixin):
    """Model representing a camp participant"""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    date_inscription = models.DateField(auto_now_add=True)
    
    # Additional fields for enhanced functionality
    photo = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    health_notes = models.TextField(blank=True, null=True)
    has_authorization = models.BooleanField(default=False, help_text="Parent's authorization to participate")
    
    class Meta:
        db_table = 'participant'
        ordering = ['nom', 'prenom']
        verbose_name = 'Participant'
        verbose_name_plural = 'Participants'
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def get_full_name(self):
        return f"{self.prenom} {self.nom}"
    
    def get_age(self):
        from datetime import date
        today = date.today()
        born = self.date_naissance
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

class ParticipantFile(TimestampMixin):
    """Model for storing documents related to participants"""
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='participant_files/')
    notes = models.TextField(blank=True, null=True)
    
    FILE_TYPES = (
        ('medical', 'Medical Document'),
        ('authorization', 'Authorization Form'),
        ('id', 'Identity Document'),
        ('other', 'Other Document'),
    )
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='other')
    
    def __str__(self):
        return f"{self.title} - {self.participant}"
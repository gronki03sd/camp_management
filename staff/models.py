from django.db import models
from django.contrib.auth.models import User
from core.models import TimestampMixin

class Responsable(TimestampMixin):
    """Model representing camp supervisors/managers"""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Additional fields
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='responsable_profile')
    date_embauche = models.DateField(blank=True, null=True)
    #photo = models.ImageField(upload_to='responsable_photos/', blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'responsable'
        verbose_name = 'Responsable'
        verbose_name_plural = 'Responsables'
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

class Animateur(TimestampMixin):
    """Model representing camp animators/activity leaders"""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    competence = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Additional fields
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='animateur_profile')
    date_embauche = models.DateField(blank=True, null=True)
    #photo = models.ImageField(upload_to='animateur_photos/', blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'animateur'
        verbose_name = 'Animateur'
        verbose_name_plural = 'Animateurs'
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

class StaffSchedule(TimestampMixin):
    """Model for managing staff schedules"""
    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE, null=True, blank=True, related_name='schedules')
    animateur = models.ForeignKey(Animateur, on_delete=models.CASCADE, null=True, blank=True, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        staff = self.responsable if self.responsable else self.animateur
        return f"{staff} - {self.date} ({self.start_time} to {self.end_time})"
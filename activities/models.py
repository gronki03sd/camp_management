from django.db import models
from core.models import TimestampMixin
from staff.models import Responsable, Animateur
from infrastructure.models import Infrastructure, Materiel
from participants.models import Participant

class Activite(TimestampMixin):
    """Model representing camp activities"""
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duree = models.IntegerField(help_text="Durée en minutes")
    date_debut = models.DateTimeField()
    responsable = models.ForeignKey(Responsable, on_delete=models.SET_NULL, null=True, related_name='activites')
    infrastructure = models.ForeignKey(Infrastructure, on_delete=models.SET_NULL, null=True, blank=True, related_name='activites')
    capacite_max = models.IntegerField(blank=True, null=True)
    
    # Additional fields
    date_fin = models.DateTimeField(blank=True, null=True)
    niveau_difficulte = models.CharField(max_length=20, blank=True, null=True)
    age_minimum = models.IntegerField(blank=True, null=True)
    age_maximum = models.IntegerField(blank=True, null=True)
    annulee = models.BooleanField(default=False)
    raison_annulation = models.TextField(blank=True, null=True)
    points_cles = models.TextField(blank=True, null=True)
   # image = models.ImageField(upload_to='activite_images/', blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'activite'
        verbose_name = 'Activité'
        verbose_name_plural = 'Activités'
        ordering = ['date_debut']
    
    def __str__(self):
        return f"{self.nom} - {self.date_debut.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate end time if not set
        if not self.date_fin and self.date_debut and self.duree:
            from datetime import timedelta
            self.date_fin = self.date_debut + timedelta(minutes=self.duree)
        super().save(*args, **kwargs)
    
    def get_participants_count(self):
        return self.inscriptions.count()
    
    def get_available_spots(self):
        if self.capacite_max:
            return max(0, self.capacite_max - self.get_participants_count())
        return None
    
    def is_full(self):
        if self.capacite_max:
            return self.get_participants_count() >= self.capacite_max
        return False

class ActiviteAnimateur(TimestampMixin):
    """Many-to-many relationship between activities and animators"""
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='animateurs_relation')
    animateur = models.ForeignKey(Animateur, on_delete=models.CASCADE, related_name='activites_relation')
    role = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'activite_animateur'
        unique_together = ('activite', 'animateur')
    
    def __str__(self):
        return f"{self.animateur} - {self.activite}"

class ActiviteMateriel(TimestampMixin):
    """Many-to-many relationship between activities and materials, with quantity"""
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='materiels_relation')
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE, related_name='activites_relation')
    quantite_requise = models.IntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'activite_materiel'
        unique_together = ('activite', 'materiel')
    
    def __str__(self):
        return f"{self.materiel} (x{self.quantite_requise}) - {self.activite}"

class Inscription(TimestampMixin):
    """Model representing participant registrations for activities"""
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='inscriptions')
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='inscriptions')
    date_inscription = models.DateTimeField(auto_now_add=True)
    STATUT_CHOICES = (
        ('inscrit', 'Inscrit'),
        ('en_attente', 'En attente'),
        ('annule', 'Annulé'),
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='inscrit')
    notes = models.TextField(blank=True, null=True)
    a_participe = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'inscription'
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        unique_together = ('participant', 'activite')
    
    def __str__(self):
        return f"{self.participant} - {self.activite}"
from django.db import models
from core.models import TimestampMixin

class Infrastructure(TimestampMixin):
    """Model representing physical infrastructures available at the camp"""
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    capacite = models.IntegerField(blank=True, null=True)
    localisation = models.CharField(max_length=100, blank=True, null=True)
    disponible = models.BooleanField(default=True)
    
    # Additional fields
    description = models.TextField(blank=True, null=True)
    #photo = models.ImageField(upload_to='infrastructure_photos/', blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    maintenance_notes = models.TextField(blank=True, null=True)
    last_maintenance_date = models.DateField(blank=True, null=True)
    next_maintenance_date = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'infrastructure'
        verbose_name = 'Infrastructure'
        verbose_name_plural = 'Infrastructures'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.type})"

class Materiel(TimestampMixin):
    """Model representing equipment/material available for activities"""
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quantite_disponible = models.IntegerField(default=0)
    
    # Additional fields
    condition = models.CharField(max_length=50, blank=True, null=True)
    #photo = models.ImageField(upload_to='materiel_photos/', blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    date_achat = models.DateField(blank=True, null=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fournisseur = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'materiel'
        verbose_name = 'Matériel'
        verbose_name_plural = 'Matériels'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} (Qté: {self.quantite_disponible})"

class InfrastructureReservation(TimestampMixin):
    """Model for managing infrastructure reservations outside of regular activities"""
    infrastructure = models.ForeignKey(Infrastructure, on_delete=models.CASCADE, related_name='reservations')
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    motif = models.CharField(max_length=255)
    responsable = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.infrastructure} - {self.date_debut.date()}"
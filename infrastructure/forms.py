from django import forms
from django.utils import timezone
from datetime import timedelta

from .models import Infrastructure, Materiel, InfrastructureReservation


class InfrastructureForm(forms.ModelForm):
    """Form for Infrastructure model"""
    class Meta:
        model = Infrastructure
        fields = [
            'nom', 'type', 'capacite', 'localisation', 'disponible',
            'description', 'photo', 'maintenance_notes', 
            'last_maintenance_date', 'next_maintenance_date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'maintenance_notes': forms.Textarea(attrs={'rows': 3}),
            'last_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        last_maintenance = cleaned_data.get('last_maintenance_date')
        next_maintenance = cleaned_data.get('next_maintenance_date')
        
        if last_maintenance and next_maintenance and last_maintenance > next_maintenance:
            self.add_error('next_maintenance_date', 
                          "La date de prochaine maintenance doit être postérieure à la dernière maintenance.")
        
        return cleaned_data


class MaterielForm(forms.ModelForm):
    """Form for Materiel model"""
    class Meta:
        model = Materiel
        fields = [
            'nom', 'description', 'quantite_disponible',
            'condition', 'photo', 'date_achat', 
            'prix_unitaire', 'fournisseur'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date_achat': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_quantite_disponible(self):
        quantite = self.cleaned_data.get('quantite_disponible')
        if quantite < 0:
            raise forms.ValidationError("La quantité ne peut pas être négative.")
        return quantite
    
    def clean_prix_unitaire(self):
        prix = self.cleaned_data.get('prix_unitaire')
        if prix is not None and prix < 0:
            raise forms.ValidationError("Le prix ne peut pas être négatif.")
        return prix


class InfrastructureReservationForm(forms.ModelForm):
    """Form for reserving an infrastructure"""
    class Meta:
        model = InfrastructureReservation
        fields = ['date_debut', 'date_fin', 'motif', 'responsable', 'notes']
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        now = timezone.now()
        # Round to next hour
        rounded_start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        rounded_end = rounded_start + timedelta(hours=2)
        
        self.fields['date_debut'].initial = rounded_start
        self.fields['date_fin'].initial = rounded_end
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('date_debut')
        end = cleaned_data.get('date_fin')
        
        if start and end:
            if start >= end:
                self.add_error('date_fin', 
                              "La date de fin doit être postérieure à la date de début.")
            
            if start < timezone.now():
                self.add_error('date_debut', 
                              "La date de début ne peut pas être dans le passé.")
            
            # Check if there are any overlapping reservations
            if 'infrastructure' in self.initial and start and end:
                infrastructure = self.initial['infrastructure']
                
                overlapping = InfrastructureReservation.objects.filter(
                    infrastructure=infrastructure,
                    date_fin__gt=start,
                    date_debut__lt=end
                )
                
                # Exclude current instance for updates
                if self.instance.pk:
                    overlapping = overlapping.exclude(pk=self.instance.pk)
                
                if overlapping.exists():
                    self.add_error(None, 
                                  "Cette période chevauche une réservation existante.")
            
            # Check if there are any activities scheduled during this time
            if 'infrastructure' in self.initial and start and end:
                from activities.models import Activite
                
                infrastructure = self.initial['infrastructure']
                
                activities = Activite.objects.filter(
                    infrastructure=infrastructure,
                    date_fin__gt=start,
                    date_debut__lt=end,
                    annulee=False
                )
                
                if activities.exists():
                    activity_names = ", ".join([a.nom for a in activities[:3]])
                    if activities.count() > 3:
                        activity_names += f" et {activities.count() - 3} autre(s)"
                    
                    self.add_error(None, 
                                  f"Des activités sont programmées pendant cette période: {activity_names}")
        
        return cleaned_data
    
from django import forms
from django.utils import timezone
from datetime import timedelta

from .models import Activite, Inscription, ActiviteAnimateur, ActiviteMateriel
from participants.models import Participant
from staff.models import Animateur
from infrastructure.models import Materiel


class ActiviteForm(forms.ModelForm):
    """Form for Activite model"""
    class Meta:
        model = Activite
        fields = [
            'nom', 'description', 'duree', 'date_debut', 'responsable', 
            'infrastructure', 'capacite_max', 'niveau_difficulte', 
            'age_minimum', 'age_maximum', 'points_cles', 'image'
        ]
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'points_cles': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['duree'].help_text = "Durée en minutes"
        self.fields['capacite_max'].help_text = "Nombre maximum de participants (laisser vide si illimité)"
        
        # Default values
        if not self.instance.pk:  # Only for new instances
            now = timezone.now()
            rounded_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            self.fields['date_debut'].initial = rounded_hour


class InscriptionForm(forms.ModelForm):
    """Form for Inscription model"""
    class Meta:
        model = Inscription
        fields = ['participant', 'activite', 'statut', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, activities_queryset=None, participants_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if activities_queryset is not None:
            self.fields['activite'].queryset = activities_queryset
        
        if participants_queryset is not None:
            self.fields['participant'].queryset = participants_queryset
        
        # Order participants by name
        if 'participant' in self.fields and participants_queryset is None:
            self.fields['participant'].queryset = Participant.objects.all().order_by('nom', 'prenom')


class ActiviteAnimateurForm(forms.ModelForm):
    """Form for adding an animator to an activity"""
    class Meta:
        model = ActiviteAnimateur
        fields = ['animateur', 'role', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, animateurs_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if animateurs_queryset is not None:
            self.fields['animateur'].queryset = animateurs_queryset
        else:
            self.fields['animateur'].queryset = Animateur.objects.filter(is_active=True).order_by('nom', 'prenom')


class ActiviteMaterielForm(forms.ModelForm):
    """Form for adding material to an activity"""
    class Meta:
        model = ActiviteMateriel
        fields = ['materiel', 'quantite_requise', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, materiels_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if materiels_queryset is not None:
            self.fields['materiel'].queryset = materiels_queryset
        else:
            # Only show materials with available quantity
            self.fields['materiel'].queryset = Materiel.objects.filter(
                quantite_disponible__gt=0
            ).order_by('nom')
        
        self.fields['quantite_requise'].initial = 1
        self.fields['quantite_requise'].widget.attrs['min'] = 1
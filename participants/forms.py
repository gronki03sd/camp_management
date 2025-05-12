from django import forms
from django.utils import timezone
from datetime import date, timedelta

from .models import Participant, ParticipantFile


class ParticipantForm(forms.ModelForm):
    """Form for Participant model"""
    class Meta:
        model = Participant
        fields = [
            'nom', 'prenom', 'date_naissance', 'adresse', 'telephone', 
            'email', 'photo', 'emergency_contact_name', 'emergency_contact_phone', 
            'health_notes', 'has_authorization'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'health_notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['date_naissance'].help_text = "Format: JJ/MM/AAAA"
        self.fields['health_notes'].help_text = "Allergies, restrictions, médicaments, etc."
        self.fields['emergency_contact_name'].help_text = "Personne à contacter en cas d'urgence"
        self.fields['has_authorization'].help_text = "Le participant a-t-il une autorisation parentale?"
        
        # Default values
        if not self.instance.pk:  # Only for new instances
            # Default to 12 years ago for date_naissance
            self.fields['date_naissance'].initial = timezone.now().date() - timedelta(days=365 * 12)
    
    def clean_date_naissance(self):
        """Validate that the birth date is not in the future"""
        dob = self.cleaned_data.get('date_naissance')
        if dob and dob > date.today():
            raise forms.ValidationError("La date de naissance ne peut pas être dans le futur.")
        return dob


class ParticipantFileForm(forms.ModelForm):
    """Form for uploading files related to a participant"""
    class Meta:
        model = ParticipantFile
        fields = ['title', 'file', 'file_type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
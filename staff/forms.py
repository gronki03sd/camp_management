from django import forms
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Responsable, Animateur, StaffSchedule


class ResponsableForm(forms.ModelForm):
    """Form for Responsable model"""
    class Meta:
        model = Responsable
        fields = [
            'nom', 'prenom', 'specialite', 'telephone', 'email',
            'date_embauche', 'photo', 'is_active', 'notes'
        ]
        widgets = {
            'date_embauche': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for new instances
        if not self.instance.pk:
            self.fields['date_embauche'].initial = timezone.now().date()
            self.fields['is_active'].initial = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if this email is already used by a User or another staff member
        if self.instance.pk:  # This is an update
            if User.objects.filter(email=email).exclude(responsable_profile=self.instance).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre utilisateur.")
            
            if Responsable.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre responsable.")
            
            if Animateur.objects.filter(email=email).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un animateur.")
        else:  # This is a create
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre utilisateur.")
            
            if Responsable.objects.filter(email=email).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre responsable.")
            
            if Animateur.objects.filter(email=email).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un animateur.")
        
        return email


class AnimateurForm(forms.ModelForm):
    """Form for Animateur model"""
    class Meta:
        model = Animateur
        fields = [
            'nom', 'prenom', 'competence', 'telephone', 'email',
            'date_embauche', 'photo', 'is_active', 'notes'
        ]
        widgets = {
            'date_embauche': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for new instances
        if not self.instance.pk:
            self.fields['date_embauche'].initial = timezone.now().date()
            self.fields['is_active'].initial = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if this email is already used by a User or another staff member
        if self.instance.pk:  # This is an update
            if User.objects.filter(email=email).exclude(animateur_profile=self.instance).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre utilisateur.")
            
            if Animateur.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre animateur.")
            
            if Responsable.objects.filter(email=email).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un responsable.")
        else:  # This is a create
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre utilisateur.")
            
            if Animateur.objects.filter(email=email).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre animateur.")
            
            if Responsable.objects.filter(email=email).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un responsable.")
        
        return email


class StaffScheduleForm(forms.ModelForm):
    """Form for StaffSchedule model"""
    class Meta:
        model = StaffSchedule
        fields = ['date', 'start_time', 'end_time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
            # Set default start time to 9:00
            self.fields['start_time'].initial = timezone.datetime.strptime('09:00', '%H:%M').time()
            # Set default end time to 17:00
            self.fields['end_time'].initial = timezone.datetime.strptime('17:00', '%H:%M').time()
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 
                          "L'heure de fin doit être postérieure à l'heure de début.")
        
        if date and date < timezone.now().date():
            self.add_error('date', 
                          "La date ne peut pas être dans le passé.")
        
        return cleaned_data
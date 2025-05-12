from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone

from .models import Activite, ActiviteAnimateur, ActiviteMateriel, Inscription
from .forms import ActiviteForm, InscriptionForm, ActiviteAnimateurForm, ActiviteMaterielForm
from participants.models import Participant
from staff.models import Responsable, Animateur
from infrastructure.models import Infrastructure, Materiel


class ActiviteListView(LoginRequiredMixin, ListView):
    """View for listing activities with filters"""
    model = Activite
    template_name = 'activities/list.html'
    context_object_name = 'activities'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Activite.objects.all()
        
        # Search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) |
                Q(description__icontains=query) |
                Q(responsable__nom__icontains=query) |
                Q(responsable__prenom__icontains=query)
            )
        
        # Date filter
        date_filter = self.request.GET.get('date_filter')
        today = timezone.now().date()
        
        if date_filter == 'today':
            queryset = queryset.filter(date_debut__date=today)
        elif date_filter == 'this_week':
            queryset = queryset.filter(
                date_debut__date__gte=today,
                date_debut__date__lte=today + timezone.timedelta(days=7)
            )
        elif date_filter == 'this_month':
            queryset = queryset.filter(
                date_debut__date__gte=today,
                date_debut__date__lte=today + timezone.timedelta(days=30)
            )
        elif date_filter == 'past':
            queryset = queryset.filter(date_debut__date__lt=today)
        elif date_filter == 'future':
            queryset = queryset.filter(date_debut__date__gte=today)
        
        # Responsable filter
        responsable_id = self.request.GET.get('responsable')
        if responsable_id:
            queryset = queryset.filter(responsable_id=responsable_id)
        
        # Sort
        sort = self.request.GET.get('sort', 'date')
        if sort == 'name':
            queryset = queryset.order_by('nom')
        elif sort == 'date':
            queryset = queryset.order_by('date_debut')
        elif sort == 'participants':
            queryset = queryset.annotate(participants_count=Count('inscriptions')).order_by('-participants_count')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responsables'] = Responsable.objects.all()
        
        # Add query parameters for pagination
        query_params = {}
        for key in ['q', 'date_filter', 'responsable', 'sort']:
            if self.request.GET.get(key):
                query_params[key] = self.request.GET.get(key)
        
        context['query_params'] = query_params
        
        return context


class ActiviteDetailView(LoginRequiredMixin, DetailView):
    """View for displaying activity details"""
    model = Activite
    template_name = 'activities/detail.html'
    context_object_name = 'activity'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = self.get_object()
        
        # Get animateurs for this activity
        context['animateurs'] = ActiviteAnimateur.objects.filter(activite=activity).select_related('animateur')
        
        # Get materials for this activity
        context['materials'] = ActiviteMateriel.objects.filter(activite=activity).select_related('materiel')
        
        # Get participants
        context['inscriptions'] = Inscription.objects.filter(activite=activity).select_related('participant')
        
        return context


class ActiviteCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new activity"""
    model = Activite
    form_class = ActiviteForm
    template_name = 'activities/form.html'
    success_url = reverse_lazy('activities:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créer une activité'
        context['button_text'] = 'Créer'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Activité créée avec succès.')
        return super().form_valid(form)


class ActiviteUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing activity"""
    model = Activite
    form_class = ActiviteForm
    template_name = 'activities/form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier l\'activité'
        context['button_text'] = 'Mettre à jour'
        return context
    
    def get_success_url(self):
        return reverse('activities:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Activité mise à jour avec succès.')
        return super().form_valid(form)


class ActiviteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting an activity"""
    model = Activite
    template_name = 'activities/confirm_delete.html'
    success_url = reverse_lazy('activities:list')
    context_object_name = 'activity'
    
    def test_func(self):
        # Only admin users can delete activities
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Activité supprimée avec succès.')
        return super().delete(request, *args, **kwargs)


class InscriptionListView(LoginRequiredMixin, ListView):
    """View for listing all inscriptions"""
    model = Inscription
    template_name = 'activities/inscription_list.html'
    context_object_name = 'inscriptions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Inscription.objects.select_related('participant', 'activite')
        
        # Search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(participant__nom__icontains=query) |
                Q(participant__prenom__icontains=query) |
                Q(activite__nom__icontains=query)
            )
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(statut=status)
        
        # Activity filter
        activity = self.request.GET.get('activity')
        if activity:
            queryset = queryset.filter(activite_id=activity)
        
        # Sort
        sort = self.request.GET.get('sort', '-date_inscription')
        queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = Activite.objects.all()
        
        # Add query parameters for pagination
        query_params = {}
        for key in ['q', 'status', 'activity', 'sort']:
            if self.request.GET.get(key):
                query_params[key] = self.request.GET.get(key)
        
        context['query_params'] = query_params
        
        return context


class InscriptionCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new inscription"""
    model = Inscription
    form_class = InscriptionForm
    template_name = 'activities/inscription_form.html'
    success_url = reverse_lazy('activities:inscription_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Only show future activities
        now = timezone.now()
        kwargs['activities_queryset'] = Activite.objects.filter(
            date_debut__gte=now, 
            annulee=False
        ).order_by('date_debut')
        return kwargs
    
    def form_valid(self, form):
        # Check if activity is full
        activite = form.cleaned_data['activite']
        if activite.is_full():
            form.add_error('activite', 'Cette activité est complète.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Inscription créée avec succès.')
        return super().form_valid(form)


class InscriptionUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an inscription"""
    model = Inscription
    form_class = InscriptionForm
    template_name = 'activities/inscription_form.html'
    success_url = reverse_lazy('activities:inscription_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # For update, include the current activity in the queryset
        now = timezone.now()
        current_activity = self.object.activite
        kwargs['activities_queryset'] = Activite.objects.filter(
            Q(date_debut__gte=now, annulee=False) | Q(id=current_activity.id)
        ).distinct().order_by('date_debut')
        return kwargs
    
    def form_valid(self, form):
        if form.cleaned_data['activite'] != self.object.activite:
            # Activity changed, check if new activity is full
            activite = form.cleaned_data['activite']
            if activite.is_full():
                form.add_error('activite', 'Cette activité est complète.')
                return self.form_invalid(form)
        
        messages.success(self.request, 'Inscription mise à jour avec succès.')
        return super().form_valid(form)


class InscriptionDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting an inscription"""
    model = Inscription
    template_name = 'activities/inscription_confirm_delete.html'
    success_url = reverse_lazy('activities:inscription_list')
    context_object_name = 'inscription'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Inscription supprimée avec succès.')
        return super().delete(request, *args, **kwargs)


class ActiviteAnimateurCreateView(LoginRequiredMixin, CreateView):
    """View for adding an animator to an activity"""
    model = ActiviteAnimateur
    form_class = ActiviteAnimateurForm
    template_name = 'activities/animateur_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        initial['activite'] = get_object_or_404(Activite, pk=self.kwargs['pk'])
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Filter out animators already assigned to this activity
        activite = get_object_or_404(Activite, pk=self.kwargs['pk'])
        existing_animateurs = ActiviteAnimateur.objects.filter(
            activite=activite
        ).values_list('animateur_id', flat=True)
        
        kwargs['animateurs_queryset'] = Animateur.objects.exclude(
            id__in=existing_animateurs
        )
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activite = get_object_or_404(Activite, pk=self.kwargs['pk'])
        context['activite'] = activite
        context['title'] = f'Ajouter un animateur à {activite.nom}'
        return context
    
    def form_valid(self, form):
        form.instance.activite = get_object_or_404(Activite, pk=self.kwargs['pk'])
        messages.success(self.request, 'Animateur ajouté avec succès.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('activities:detail', kwargs={'pk': self.kwargs['pk']})


class ActiviteMaterielCreateView(LoginRequiredMixin, CreateView):
    """View for adding material to an activity"""
    model = ActiviteMateriel
    form_class = ActiviteMaterielForm
    template_name = 'activities/materiel_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        initial['activite'] = get_object_or_404(Activite, pk=self.kwargs['pk'])
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Filter out materials already assigned to this activity
        activite = get_object_or_404(Activite, pk=self.kwargs['pk'])
        existing_materiels = ActiviteMateriel.objects.filter(
            activite=activite
        ).values_list('materiel_id', flat=True)
        
        kwargs['materiels_queryset'] = Materiel.objects.exclude(
            id__in=existing_materiels
        )
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activite = get_object_or_404(Activite, pk=self.kwargs['pk'])
        context['activite'] = activite
        context['title'] = f'Ajouter du matériel à {activite.nom}'
        return context
    
    def form_valid(self, form):
        # Check if there's enough material available
        materiel = form.cleaned_data['materiel']
        quantite_requise = form.cleaned_data['quantite_requise']
        
        if materiel.quantite_disponible < quantite_requise:
            form.add_error('quantite_requise', 
                           f'Quantité insuffisante. Disponible: {materiel.quantite_disponible}')
            return self.form_invalid(form)
        
        form.instance.activite = get_object_or_404(Activite, pk=self.kwargs['pk'])
        messages.success(self.request, 'Matériel ajouté avec succès.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('activities:detail', kwargs={'pk': self.kwargs['pk']})


class ActiviteAnimateurDeleteView(LoginRequiredMixin, DeleteView):
    """View for removing an animator from an activity"""
    model = ActiviteAnimateur
    template_name = 'activities/animateur_confirm_delete.html'
    context_object_name = 'animateur_relation'
    
    def get_success_url(self):
        return reverse('activities:detail', kwargs={'pk': self.object.activite.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Animateur retiré avec succès.')
        return super().delete(request, *args, **kwargs)


class ActiviteMaterielDeleteView(LoginRequiredMixin, DeleteView):
    """View for removing material from an activity"""
    model = ActiviteMateriel
    template_name = 'activities/materiel_confirm_delete.html'
    context_object_name = 'materiel_relation'
    
    def get_success_url(self):
        return reverse('activities:detail', kwargs={'pk': self.object.activite.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Matériel retiré avec succès.')
        return super().delete(request, *args, **kwargs)


class ParticipantActivitiesView(LoginRequiredMixin, ListView):
    """View for displaying activities of a specific participant"""
    template_name = 'activities/participant_activities.html'
    context_object_name = 'inscriptions'
    
    def get_queryset(self):
        self.participant = get_object_or_404(Participant, pk=self.kwargs['pk'])
        return Inscription.objects.filter(participant=self.participant).select_related('activite')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participant'] = self.participant
        
        # Get future activities where this participant is not already registered
        now = timezone.now()
        existing_activities = Inscription.objects.filter(
            participant=self.participant
        ).values_list('activite_id', flat=True)
        
        available_activities = Activite.objects.filter(
            date_debut__gte=now,
            annulee=False
        ).exclude(
            id__in=existing_activities
        ).order_by('date_debut')
        
        context['available_activities'] = available_activities
        return context


class QuickInscriptionView(LoginRequiredMixin, FormView):
    """View for quickly registering a participant to an activity"""
    template_name = 'activities/quick_inscription.html'
    form_class = InscriptionForm
    
    def get_initial(self):
        initial = super().get_initial()
        participant_id = self.kwargs.get('participant_id')
        activity_id = self.kwargs.get('activity_id')
        
        if participant_id:
            initial['participant'] = get_object_or_404(Participant, pk=participant_id)
        
        if activity_id:
            initial['activite'] = get_object_or_404(Activite, pk=activity_id)
        
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        now = timezone.now()
        
        # When participant is preselected, only show future activities where they're not registered
        participant_id = self.kwargs.get('participant_id')
        if participant_id:
            participant = get_object_or_404(Participant, pk=participant_id)
            existing_activities = Inscription.objects.filter(
                participant=participant
            ).values_list('activite_id', flat=True)
            
            kwargs['activities_queryset'] = Activite.objects.filter(
                date_debut__gte=now,
                annulee=False
            ).exclude(
                id__in=existing_activities
            ).order_by('date_debut')
        else:
            # When no participant is preselected, show all future activities
            kwargs['activities_queryset'] = Activite.objects.filter(
                date_debut__gte=now, 
                annulee=False
            ).order_by('date_debut')
        
        # When activity is preselected, only show participants not already registered
        activity_id = self.kwargs.get('activity_id')
        if activity_id:
            activity = get_object_or_404(Activite, pk=activity_id)
            existing_participants = Inscription.objects.filter(
                activite=activity
            ).values_list('participant_id', flat=True)
            
            kwargs['participants_queryset'] = Participant.objects.exclude(
                id__in=existing_participants
            ).order_by('nom', 'prenom')
        
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        participant_id = self.kwargs.get('participant_id')
        activity_id = self.kwargs.get('activity_id')
        
        if participant_id:
            context['participant'] = get_object_or_404(Participant, pk=participant_id)
        
        if activity_id:
            context['activity'] = get_object_or_404(Activite, pk=activity_id)
        
        return context
    
    def form_valid(self, form):
        # Check if activity is full
        activite = form.cleaned_data['activite']
        if activite.is_full():
            form.add_error('activite', 'Cette activité est complète.')
            return self.form_invalid(form)
        
        # Check if inscription already exists
        participant = form.cleaned_data['participant']
        existing = Inscription.objects.filter(
            participant=participant,
            activite=activite
        ).exists()
        
        if existing:
            form.add_error(None, 'Ce participant est déjà inscrit à cette activité.')
            return self.form_invalid(form)
        
        # Create inscription
        inscription = form.save()
        messages.success(self.request, 'Inscription créée avec succès.')
        
        # Determine redirect URL
        participant_id = self.kwargs.get('participant_id')
        activity_id = self.kwargs.get('activity_id')
        
        if participant_id:
            return redirect('activities:participant_activities', pk=participant_id)
        elif activity_id:
            return redirect('activities:detail', pk=activity_id)
        else:
            return redirect('activities:inscription_list')
        
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de l\'inscription. Veuillez vérifier les informations.')
        return super().form_invalid(form)


def check_activity_capacity(request, pk):
    """AJAX view to check if an activity has available capacity"""
    try:
        activity = Activite.objects.get(pk=pk)
        available = activity.get_available_spots()
        is_full = activity.is_full()
        
        return JsonResponse({
            'success': True,
            'is_full': is_full,
            'available_spots': available,
            'total_capacity': activity.capacite_max,
            'current_participants': activity.get_participants_count()
        })
    except Activite.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Activity not found'
        }, status=404)
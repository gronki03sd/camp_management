from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone

from .models import Participant, ParticipantFile
from .forms import ParticipantForm, ParticipantFileForm
from activities.models import Inscription, Activite


class ParticipantListView(LoginRequiredMixin, ListView):
    """View for listing participants with search and filters"""
    model = Participant
    template_name = 'participants/list.html'
    context_object_name = 'participants'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Participant.objects.all()
        
        # Search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) |
                Q(prenom__icontains=query) |
                Q(email__icontains=query) |
                Q(telephone__icontains=query)
            )
        
        # Age filter
        age_filter = self.request.GET.get('age')
        if age_filter:
            today = timezone.now().date()
            if age_filter == 'child':  # Under 12
                max_date = today.replace(year=today.year - 12)
                queryset = queryset.filter(date_naissance__gt=max_date)
            elif age_filter == 'teen':  # 12-17
                min_date = today.replace(year=today.year - 18)
                max_date = today.replace(year=today.year - 12)
                queryset = queryset.filter(date_naissance__gt=min_date, date_naissance__lte=max_date)
            elif age_filter == 'adult':  # 18+
                min_date = today.replace(year=today.year - 18)
                queryset = queryset.filter(date_naissance__lte=min_date)
        
        # Sort
        sort = self.request.GET.get('sort', 'nom')
        if sort == 'name':
            queryset = queryset.order_by('nom', 'prenom')
        elif sort == 'age':
            queryset = queryset.order_by('date_naissance')
        elif sort == 'inscription':
            queryset = queryset.order_by('-date_inscription')
        elif sort == 'activities':
            queryset = queryset.annotate(
                activities_count=Count('inscriptions')
            ).order_by('-activities_count')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add query parameters for pagination
        query_params = {}
        for key in ['q', 'age', 'sort']:
            if self.request.GET.get(key):
                query_params[key] = self.request.GET.get(key)
        
        context['query_params'] = query_params
        
        # Add active filters for UI
        context['age_filter'] = self.request.GET.get('age', '')
        context['sort'] = self.request.GET.get('sort', 'nom')
        
        return context


class ParticipantDetailView(LoginRequiredMixin, DetailView):
    """View for displaying participant details"""
    model = Participant
    template_name = 'participants/detail.html'
    context_object_name = 'participant'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participant = self.get_object()
        
        # Get participant's activities
        now = timezone.now()
        
        context['upcoming_activities'] = Inscription.objects.filter(
            participant=participant,
            activite__date_debut__gte=now
        ).select_related('activite').order_by('activite__date_debut')
        
        context['past_activities'] = Inscription.objects.filter(
            participant=participant,
            activite__date_debut__lt=now
        ).select_related('activite').order_by('-activite__date_debut')
        
        # Get participant's files
        context['files'] = ParticipantFile.objects.filter(participant=participant)
        
        # Calculate age
        context['age'] = participant.get_age()
        
        return context


class ParticipantCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new participant"""
    model = Participant
    form_class = ParticipantForm
    template_name = 'participants/form.html'
    success_url = reverse_lazy('participants:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un participant'
        context['button_text'] = 'Ajouter'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Participant ajouté avec succès.')
        return super().form_valid(form)


class ParticipantUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing participant"""
    model = Participant
    form_class = ParticipantForm
    template_name = 'participants/form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le participant'
        context['button_text'] = 'Mettre à jour'
        return context
    
    def get_success_url(self):
        return reverse('participants:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Participant mis à jour avec succès.')
        return super().form_valid(form)


class ParticipantDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a participant"""
    model = Participant
    template_name = 'participants/confirm_delete.html'
    success_url = reverse_lazy('participants:list')
    context_object_name = 'participant'
    
    def test_func(self):
        # Only staff users can delete
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Participant supprimé avec succès.')
        return super().delete(request, *args, **kwargs)


class ParticipantFileCreateView(LoginRequiredMixin, CreateView):
    """View for adding a file to a participant"""
    model = ParticipantFile
    form_class = ParticipantFileForm
    template_name = 'participants/file_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        initial['participant'] = get_object_or_404(Participant, pk=self.kwargs['pk'])
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participant = get_object_or_404(Participant, pk=self.kwargs['pk'])
        context['participant'] = participant
        context['title'] = f'Ajouter un document pour {participant.get_full_name()}'
        return context
    
    def form_valid(self, form):
        form.instance.participant = get_object_or_404(Participant, pk=self.kwargs['pk'])
        messages.success(self.request, 'Document ajouté avec succès.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('participants:detail', kwargs={'pk': self.kwargs['pk']})


class ParticipantFileDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a participant file"""
    model = ParticipantFile
    template_name = 'participants/file_confirm_delete.html'
    context_object_name = 'file'
    
    def get_success_url(self):
        return reverse('participants:detail', kwargs={'pk': self.object.participant.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document supprimé avec succès.')
        return super().delete(request, *args, **kwargs)


def participant_activities_json(request, pk):
    """AJAX view to get participant's activities as JSON for calendar"""
    participant = get_object_or_404(Participant, pk=pk)
    inscriptions = Inscription.objects.filter(
        participant=participant
    ).select_related('activite')
    
    events = []
    for inscription in inscriptions:
        activite = inscription.activite
        events.append({
            'id': activite.id,
            'title': activite.nom,
            'start': activite.date_debut.isoformat(),
            'end': activite.date_fin.isoformat() if activite.date_fin else None,
            'url': reverse('activities:detail', kwargs={'pk': activite.id}),
            'backgroundColor': '#4F46E5',  # Indigo
            'borderColor': '#4338CA',
        })
    
    return JsonResponse(events, safe=False)
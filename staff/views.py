from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse

from .models import Responsable, Animateur, StaffSchedule
from .forms import ResponsableForm, AnimateurForm, StaffScheduleForm
from activities.models import Activite, ActiviteAnimateur


class StaffDashboardView(LoginRequiredMixin, TemplateView):
    """View for staff dashboard"""
    template_name = 'staff/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # General stats
        context['total_responsables'] = Responsable.objects.count()
        context['total_animateurs'] = Animateur.objects.count()
        
        # Active staff count
        context['active_responsables'] = Responsable.objects.filter(is_active=True).count()
        context['active_animateurs'] = Animateur.objects.filter(is_active=True).count()
        
        # Recent activities
        now = timezone.now()
        context['upcoming_activities'] = Activite.objects.filter(
            date_debut__gte=now,
            annulee=False
        ).select_related('responsable').order_by('date_debut')[:5]
        
        # Top animateurs by activity count
        top_animateurs = Animateur.objects.annotate(
            activity_count=Count('activites_relation')
        ).order_by('-activity_count')[:5]
        
        context['top_animateurs'] = top_animateurs
        
        return context


class StaffListView(LoginRequiredMixin, ListView):
    """View for listing all staff members"""
    template_name = 'staff/list.html'
    context_object_name = 'staff_members'
    
    def get_queryset(self):
        # Search query
        query = self.request.GET.get('q')
        
        # Role filter
        role = self.request.GET.get('role', 'all')
        
        # Status filter
        status = self.request.GET.get('status', 'all')
        
        # Build responsables queryset
        responsables = Responsable.objects.all()
        if query:
            responsables = responsables.filter(
                Q(nom__icontains=query) |
                Q(prenom__icontains=query) |
                Q(email__icontains=query) |
                Q(specialite__icontains=query)
            )
        
        if status != 'all':
            is_active = (status == 'active')
            responsables = responsables.filter(is_active=is_active)
        
        # Build animateurs queryset
        animateurs = Animateur.objects.all()
        if query:
            animateurs = animateurs.filter(
                Q(nom__icontains=query) |
                Q(prenom__icontains=query) |
                Q(email__icontains=query) |
                Q(competence__icontains=query)
            )
        
        if status != 'all':
            is_active = (status == 'active')
            animateurs = animateurs.filter(is_active=is_active)
        
        # Combine based on role filter
        if role == 'responsable':
            return {'responsables': responsables, 'animateurs': []}
        elif role == 'animateur':
            return {'responsables': [], 'animateurs': animateurs}
        else:
            return {'responsables': responsables, 'animateurs': animateurs}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add query parameters for active filters
        context['query'] = self.request.GET.get('q', '')
        context['role_filter'] = self.request.GET.get('role', 'all')
        context['status_filter'] = self.request.GET.get('status', 'all')
        
        # Counts for the view
        context['responsables_count'] = context['staff_members']['responsables'].count()
        context['animateurs_count'] = context['staff_members']['animateurs'].count()
        context['total_count'] = context['responsables_count'] + context['animateurs_count']
        
        return context


class ResponsableDetailView(LoginRequiredMixin, DetailView):
    """View for displaying responsable details"""
    model = Responsable
    template_name = 'staff/responsable_detail.html'
    context_object_name = 'responsable'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        responsable = self.get_object()
        
        # Get activities for this responsable
        now = timezone.now()
        
        context['upcoming_activities'] = Activite.objects.filter(
            responsable=responsable,
            date_debut__gte=now,
            annulee=False
        ).order_by('date_debut')
        
        context['past_activities'] = Activite.objects.filter(
            responsable=responsable,
            date_debut__lt=now
        ).order_by('-date_debut')[:10]
        
        # Get work schedules
        context['schedules'] = StaffSchedule.objects.filter(
            responsable=responsable,
            date__gte=now.date()
        ).order_by('date', 'start_time')
        
        return context


class AnimateurDetailView(LoginRequiredMixin, DetailView):
    """View for displaying animateur details"""
    model = Animateur
    template_name = 'staff/animateur_detail.html'
    context_object_name = 'animateur'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        animateur = self.get_object()
        
        # Get activities for this animateur
        now = timezone.now()
        
        context['upcoming_activities'] = ActiviteAnimateur.objects.filter(
            animateur=animateur,
            activite__date_debut__gte=now,
            activite__annulee=False
        ).select_related('activite').order_by('activite__date_debut')
        
        context['past_activities'] = ActiviteAnimateur.objects.filter(
            animateur=animateur,
            activite__date_debut__lt=now
        ).select_related('activite').order_by('-activite__date_debut')[:10]
        
        # Get work schedules
        context['schedules'] = StaffSchedule.objects.filter(
            animateur=animateur,
            date__gte=now.date()
        ).order_by('date', 'start_time')
        
        return context


class ResponsableCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View for creating a new responsable"""
    model = Responsable
    form_class = ResponsableForm
    template_name = 'staff/responsable_form.html'
    success_url = reverse_lazy('staff:list')
    
    def test_func(self):
        # Only staff can create new staff members
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un responsable'
        context['button_text'] = 'Créer'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Responsable ajouté avec succès.')
        return super().form_valid(form)


class ResponsableUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing responsable"""
    model = Responsable
    form_class = ResponsableForm
    template_name = 'staff/responsable_form.html'
    
    def test_func(self):
        # Only staff can update staff members
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le responsable'
        context['button_text'] = 'Mettre à jour'
        return context
    
    def get_success_url(self):
        return reverse('staff:responsable_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Responsable mis à jour avec succès.')
        return super().form_valid(form)


class ResponsableDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a responsable"""
    model = Responsable
    template_name = 'staff/responsable_confirm_delete.html'
    success_url = reverse_lazy('staff:list')
    context_object_name = 'responsable'
    
    def test_func(self):
        # Only staff can delete staff members
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Responsable supprimé avec succès.')
        return super().delete(request, *args, **kwargs)


class AnimateurCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View for creating a new animateur"""
    model = Animateur
    form_class = AnimateurForm
    template_name = 'staff/animateur_form.html'
    success_url = reverse_lazy('staff:list')
    
    def test_func(self):
        # Only staff can create new staff members
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un animateur'
        context['button_text'] = 'Créer'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Animateur ajouté avec succès.')
        return super().form_valid(form)


class AnimateurUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing animateur"""
    model = Animateur
    form_class = AnimateurForm
    template_name = 'staff/animateur_form.html'
    
    def test_func(self):
        # Only staff can update staff members
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier l\'animateur'
        context['button_text'] = 'Mettre à jour'
        return context
    
    def get_success_url(self):
        return reverse('staff:animateur_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Animateur mis à jour avec succès.')
        return super().form_valid(form)


class AnimateurDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting an animateur"""
    model = Animateur
    template_name = 'staff/animateur_confirm_delete.html'
    success_url = reverse_lazy('staff:list')
    context_object_name = 'animateur'
    
    def test_func(self):
        # Only staff can delete staff members
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Animateur supprimé avec succès.')
        return super().delete(request, *args, **kwargs)


class StaffScheduleCreateView(LoginRequiredMixin, CreateView):
    """View for creating a schedule for a staff member"""
    model = StaffSchedule
    form_class = StaffScheduleForm
    template_name = 'staff/schedule_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.staff_type = self.kwargs.get('staff_type')
        self.staff_id = self.kwargs.get('pk')
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        self.staff_type = self.kwargs.get('staff_type')
        self.staff_id = self.kwargs.get('pk')
        
        if self.staff_type == 'responsable':
            initial['responsable'] = get_object_or_404(Responsable, pk=self.staff_id)
        elif self.staff_type == 'animateur':
            initial['animateur'] = get_object_or_404(Animateur, pk=self.staff_id)
        
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.staff_type = self.kwargs.get('staff_type')
        self.staff_id = self.kwargs.get('pk')
        
        if self.staff_type == 'responsable':
            staff_member = get_object_or_404(Responsable, pk=self.staff_id)
        elif self.staff_type == 'animateur':
            staff_member = get_object_or_404(Animateur, pk=self.staff_id)
        else:
            staff_member = None
        
        context['staff_member'] = staff_member
        context['staff_type'] = self.staff_type
        context['title'] = f'Ajouter un horaire pour {staff_member.get_full_name() if staff_member else "membre du personnel"}'
        context['button_text'] = 'Créer'
        
        return context
    
    def form_valid(self, form):
        self.staff_type = self.kwargs.get('staff_type')
        self.staff_id = self.kwargs.get('pk')
        
        if self.staff_type == 'responsable':
            form.instance.responsable = get_object_or_404(Responsable, pk=self.staff_id)
        elif self.staff_type == 'animateur':
            form.instance.animateur = get_object_or_404(Animateur, pk=self.staff_id)
        
        messages.success(self.request, 'Horaire ajouté avec succès.')
        return super().form_valid(form)
    
    def get_success_url(self):
        self.staff_type = self.kwargs.get('staff_type')
        self.staff_id = self.kwargs.get('pk')
        
        if self.staff_type == 'responsable':
            return reverse('staff:responsable_detail', kwargs={'pk': self.staff_id})
        elif self.staff_type == 'animateur':
            return reverse('staff:animateur_detail', kwargs={'pk': self.staff_id})
        
        return reverse('staff:list')


class StaffScheduleDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a staff schedule"""
    model = StaffSchedule
    template_name = 'staff/schedule_confirm_delete.html'
    context_object_name = 'schedule'
    
    def get_success_url(self):
        schedule = self.get_object()
        if schedule.responsable:
            return reverse('staff:responsable_detail', kwargs={'pk': schedule.responsable.pk})
        elif schedule.animateur:
            return reverse('staff:animateur_detail', kwargs={'pk': schedule.animateur.pk})
        
        return reverse('staff:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Horaire supprimé avec succès.')
        return super().delete(request, *args, **kwargs)


def staff_activities_json(request, staff_type, pk):
    """AJAX view to get staff member's activities as JSON for calendar"""
    now = timezone.now()
    events = []
    
    if staff_type == 'responsable':
        staff_member = get_object_or_404(Responsable, pk=pk)
        activities = Activite.objects.filter(responsable=staff_member)
        
        for activity in activities:
            events.append({
                'id': activity.id,
                'title': activity.nom,
                'start': activity.date_debut.isoformat(),
                'end': activity.date_fin.isoformat() if activity.date_fin else None,
                'url': reverse('activities:detail', kwargs={'pk': activity.id}),
                'backgroundColor': '#4F46E5' if not activity.annulee else '#EF4444',
                'borderColor': '#4338CA' if not activity.annulee else '#DC2626',
            })
    
    elif staff_type == 'animateur':
        staff_member = get_object_or_404(Animateur, pk=pk)
        activity_relations = ActiviteAnimateur.objects.filter(
            animateur=staff_member
        ).select_related('activite')
        
        for relation in activity_relations:
            activity = relation.activite
            events.append({
                'id': activity.id,
                'title': activity.nom,
                'start': activity.date_debut.isoformat(),
                'end': activity.date_fin.isoformat() if activity.date_fin else None,
                'url': reverse('activities:detail', kwargs={'pk': activity.id}),
                'backgroundColor': '#059669' if not activity.annulee else '#EF4444',
                'borderColor': '#047857' if not activity.annulee else '#DC2626',
            })
    
    # Add schedules
    schedules = StaffSchedule.objects.filter(
        Q(responsable_id=pk, animateur__isnull=True) if staff_type == 'responsable' 
        else Q(animateur_id=pk, responsable__isnull=True)
    )
    
    for schedule in schedules:
        # Create a datetime combining date with time
        start_datetime = timezone.make_aware(timezone.datetime.combine(
            schedule.date, schedule.start_time
        ))
        end_datetime = timezone.make_aware(timezone.datetime.combine(
            schedule.date, schedule.end_time
        ))
        
        events.append({
            'id': f'schedule_{schedule.id}',
            'title': f'Horaire: {schedule.notes or "Travail"}',
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'backgroundColor': '#F59E0B',
            'borderColor': '#D97706',
        })
    
    return JsonResponse(events, safe=False)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone

from .models import Infrastructure, Materiel, InfrastructureReservation
from .forms import InfrastructureForm, MaterielForm, InfrastructureReservationForm
from activities.models import Activite


class InfrastructureListView(LoginRequiredMixin, ListView):
    """View for listing all infrastructures"""
    model = Infrastructure
    template_name = 'infrastructure/list.html'
    context_object_name = 'infrastructures'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Infrastructure.objects.all()
        
        # Search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) |
                Q(type__icontains=query) |
                Q(localisation__icontains=query)
            )
        
        # Type filter
        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        # Availability filter
        availability = self.request.GET.get('disponible')
        if availability:
            if availability == 'true':
                queryset = queryset.filter(disponible=True)
            elif availability == 'false':
                queryset = queryset.filter(disponible=False)
        
        # Sort
        sort = self.request.GET.get('sort', 'nom')
        if sort == 'nom':
            queryset = queryset.order_by('nom')
        elif sort == 'capacite':
            queryset = queryset.order_by('-capacite')
        elif sort == 'type':
            queryset = queryset.order_by('type', 'nom')
        elif sort == 'activities':
            queryset = queryset.annotate(
                activity_count=Count('activites')
            ).order_by('-activity_count')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get unique types for filter
        context['types'] = Infrastructure.objects.values_list('type', flat=True).distinct()
        
        # Add query parameters for pagination
        query_params = {}
        for key in ['q', 'type', 'disponible', 'sort']:
            if self.request.GET.get(key):
                query_params[key] = self.request.GET.get(key)
        
        context['query_params'] = query_params
        
        return context


class InfrastructureDetailView(LoginRequiredMixin, DetailView):
    """View for displaying infrastructure details"""
    model = Infrastructure
    template_name = 'infrastructure/detail.html'
    context_object_name = 'infrastructure'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        infrastructure = self.get_object()
        
        # Get upcoming activities using this infrastructure
        now = timezone.now()
        context['upcoming_activities'] = Activite.objects.filter(
            infrastructure=infrastructure,
            date_debut__gte=now,
            annulee=False
        ).order_by('date_debut')[:5]
        
        # Get past activities
        context['past_activities'] = Activite.objects.filter(
            infrastructure=infrastructure,
            date_debut__lt=now
        ).order_by('-date_debut')[:5]
        
        # Get reservations
        context['reservations'] = InfrastructureReservation.objects.filter(
            infrastructure=infrastructure,
            date_fin__gte=now
        ).order_by('date_debut')
        
        return context


class InfrastructureCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new infrastructure"""
    model = Infrastructure
    form_class = InfrastructureForm
    template_name = 'infrastructure/form.html'
    success_url = reverse_lazy('infrastructure:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une infrastructure'
        context['button_text'] = 'Créer'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Infrastructure ajoutée avec succès.')
        return super().form_valid(form)


class InfrastructureUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing infrastructure"""
    model = Infrastructure
    form_class = InfrastructureForm
    template_name = 'infrastructure/form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier l\'infrastructure'
        context['button_text'] = 'Mettre à jour'
        return context
    
    def get_success_url(self):
        return reverse('infrastructure:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Infrastructure mise à jour avec succès.')
        return super().form_valid(form)


class InfrastructureDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting an infrastructure"""
    model = Infrastructure
    template_name = 'infrastructure/confirm_delete.html'
    success_url = reverse_lazy('infrastructure:list')
    context_object_name = 'infrastructure'
    
    def test_func(self):
        # Only staff can delete
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Infrastructure supprimée avec succès.')
        return super().delete(request, *args, **kwargs)


class MaterielListView(LoginRequiredMixin, ListView):
    """View for listing all materials"""
    model = Materiel
    template_name = 'infrastructure/materiel_list.html'
    context_object_name = 'materiels'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Materiel.objects.all()
        
        # Search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) |
                Q(description__icontains=query)
            )
        
        # Stock filter
        stock = self.request.GET.get('stock')
        if stock:
            if stock == 'low':
                queryset = queryset.filter(quantite_disponible__lte=5)
            elif stock == 'out':
                queryset = queryset.filter(quantite_disponible=0)
        
        # Sort
        sort = self.request.GET.get('sort', 'nom')
        if sort == 'nom':
            queryset = queryset.order_by('nom')
        elif sort == 'quantite':
            queryset = queryset.order_by('quantite_disponible')
        elif sort == 'prix':
            queryset = queryset.order_by('-prix_unitaire')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add query parameters for pagination
        query_params = {}
        for key in ['q', 'stock', 'sort']:
            if self.request.GET.get(key):
                query_params[key] = self.request.GET.get(key)
        
        context['query_params'] = query_params
        
        # Count materials with low stock
        context['low_stock_count'] = Materiel.objects.filter(quantite_disponible__lte=5).count()
        context['out_of_stock_count'] = Materiel.objects.filter(quantite_disponible=0).count()
        
        return context


class MaterielDetailView(LoginRequiredMixin, DetailView):
    """View for displaying material details"""
    model = Materiel
    template_name = 'infrastructure/materiel_detail.html'
    context_object_name = 'materiel'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        materiel = self.get_object()
        
        # Get activities using this material
        from activities.models import ActiviteMateriel
        
        context['activity_relations'] = ActiviteMateriel.objects.filter(
            materiel=materiel
        ).select_related('activite').order_by('activite__date_debut')
        
        return context


class MaterielCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new material"""
    model = Materiel
    form_class = MaterielForm
    template_name = 'infrastructure/materiel_form.html'
    success_url = reverse_lazy('infrastructure:materiel_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter du matériel'
        context['button_text'] = 'Créer'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Matériel ajouté avec succès.')
        return super().form_valid(form)


class MaterielUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing material"""
    model = Materiel
    form_class = MaterielForm
    template_name = 'infrastructure/materiel_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le matériel'
        context['button_text'] = 'Mettre à jour'
        return context
    
    def get_success_url(self):
        return reverse('infrastructure:materiel_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Matériel mis à jour avec succès.')
        return super().form_valid(form)


class MaterielDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a material"""
    model = Materiel
    template_name = 'infrastructure/materiel_confirm_delete.html'
    success_url = reverse_lazy('infrastructure:materiel_list')
    context_object_name = 'materiel'
    
    def test_func(self):
        # Only staff can delete
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Matériel supprimé avec succès.')
        return super().delete(request, *args, **kwargs)


class InfrastructureReservationCreateView(LoginRequiredMixin, CreateView):
    """View for creating a reservation for an infrastructure"""
    model = InfrastructureReservation
    form_class = InfrastructureReservationForm
    template_name = 'infrastructure/reservation_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        initial['infrastructure'] = get_object_or_404(Infrastructure, pk=self.kwargs['pk'])
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        infrastructure = get_object_or_404(Infrastructure, pk=self.kwargs['pk'])
        context['infrastructure'] = infrastructure
        context['title'] = f'Réserver {infrastructure.nom}'
        context['button_text'] = 'Réserver'
        return context
    
    def form_valid(self, form):
        form.instance.infrastructure = get_object_or_404(Infrastructure, pk=self.kwargs['pk'])
        messages.success(self.request, 'Réservation créée avec succès.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('infrastructure:detail', kwargs={'pk': self.kwargs['pk']})


class InfrastructureReservationDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a reservation"""
    model = InfrastructureReservation
    template_name = 'infrastructure/reservation_confirm_delete.html'
    context_object_name = 'reservation'
    
    def get_success_url(self):
        return reverse('infrastructure:detail', kwargs={'pk': self.object.infrastructure.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Réservation supprimée avec succès.')
        return super().delete(request, *args, **kwargs)
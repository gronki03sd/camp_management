from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, F, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

from activities.models import Activite, Inscription
from participants.models import Participant
from staff.models import Responsable, Animateur
from infrastructure.models import Infrastructure, Materiel


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view showing overview of camp activities"""
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date and date range
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Dashboard statistics
        context['total_participants'] = Participant.objects.count()
        context['total_activities'] = Activite.objects.count()
        context['upcoming_activities'] = Activite.objects.filter(
            date_debut__gte=today,
            annulee=False
        ).order_by('date_debut')[:5]
        
        context['recent_registrations'] = Inscription.objects.select_related(
            'participant', 'activite'
        ).order_by('-date_inscription')[:5]
        
        # Compare to previous period
        new_participants_week = Participant.objects.filter(
            date_inscription__gte=week_ago
        ).count()
        
        new_participants_prev_week = Participant.objects.filter(
            date_inscription__gte=week_ago - timedelta(days=7),
            date_inscription__lt=week_ago
        ).count()
        
        if new_participants_prev_week > 0:
            growth_rate = ((new_participants_week - new_participants_prev_week) / new_participants_prev_week) * 100
        else:
            growth_rate = 100 if new_participants_week > 0 else 0
            
        context['new_participants_week'] = new_participants_week
        context['participant_growth_rate'] = growth_rate
        
        # Activity statistics
        context['activities_this_week'] = Activite.objects.filter(
            date_debut__gte=today,
            date_debut__lte=today + timedelta(days=7),
            annulee=False
        ).count()
        
        context['full_activities'] = Activite.objects.filter(
            date_debut__gte=today,
            annulee=False
        ).annotate(
            participants_count=Count('inscriptions')
        ).filter(
            participants_count__gte=F('capacite_max')
        ).count()
        
        # Staff statistics
        context['total_staff'] = Responsable.objects.count() + Animateur.objects.count()
        
        # Material statistics
        context['low_stock_materials'] = Materiel.objects.filter(
            quantite_disponible__lte=5
        ).order_by('quantite_disponible')[:5]
        
        return context


class ParticipantsChartView(LoginRequiredMixin, View):
    """View to provide data for the participants chart"""
    
    def get(self, request, *args, **kwargs):
        time_period = request.GET.get('period', 'week')
        
        today = timezone.now().date()
        
        if time_period == 'week':
            # Last 7 days
            start_date = today - timedelta(days=7)
            query = Participant.objects.filter(date_inscription__gte=start_date)
            query = query.annotate(date=TruncDay('date_inscription'))
            date_format = '%d/%m'
            
        elif time_period == 'month':
            # Last 30 days
            start_date = today - timedelta(days=30)
            query = Participant.objects.filter(date_inscription__gte=start_date)
            query = query.annotate(date=TruncDay('date_inscription'))
            date_format = '%d/%m'
            
        elif time_period == 'year':
            # Last 12 months
            start_date = today - timedelta(days=365)
            query = Participant.objects.filter(date_inscription__gte=start_date)
            query = query.annotate(date=TruncMonth('date_inscription'))
            date_format = '%m/%Y'
        else:
            # All time (group by month)
            query = Participant.objects.all()
            query = query.annotate(date=TruncMonth('date_inscription'))
            date_format = '%m/%Y'
        
        # Group by date and count
        data = query.values('date').annotate(count=Count('id')).order_by('date')
        
        # Format for Chart.js
        labels = [entry['date'].strftime(date_format) if entry['date'] else 'N/A' for entry in data]
        counts = [entry['count'] for entry in data]
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'label': 'Nouveaux participants',
                'backgroundColor': 'rgba(99, 102, 241, 0.5)',
                'borderColor': 'rgb(99, 102, 241)',
                'data': counts,
            }]
        })


class ActivitiesChartView(LoginRequiredMixin, View):
    """View to provide data for the activities chart"""
    
    def get(self, request, *args, **kwargs):
        # Get top activities by participant count
        top_activities = Activite.objects.annotate(
            participants_count=Count('inscriptions')
        ).order_by('-participants_count')[:10]
        
        labels = [activity.nom for activity in top_activities]
        counts = [activity.participants_count for activity in top_activities]
        capacities = [activity.capacite_max or 0 for activity in top_activities]
        
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Participants inscrits',
                    'backgroundColor': 'rgba(99, 102, 241, 0.5)',
                    'borderColor': 'rgb(99, 102, 241)',
                    'data': counts,
                },
                {
                    'label': 'Capacité maximale',
                    'backgroundColor': 'rgba(203, 213, 225, 0.5)',
                    'borderColor': 'rgb(203, 213, 225)',
                    'data': capacities,
                }
            ]
        })


class MaterialsChartView(LoginRequiredMixin, View):
    """View to provide data for the materials chart"""
    
    def get(self, request, *args, **kwargs):
        # Get materials with low stock
        materials = Materiel.objects.order_by('quantite_disponible')[:10]
        
        labels = [material.nom for material in materials]
        quantities = [material.quantite_disponible for material in materials]
        
        # Calculate warning thresholds (for visualization)
        max_quantity = max(quantities) if quantities else 10
        thresholds = [max_quantity * 0.3] * len(labels)  # 30% of max as warning threshold
        
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Quantité disponible',
                    'backgroundColor': 'rgba(99, 102, 241, 0.5)',
                    'borderColor': 'rgb(99, 102, 241)',
                    'data': quantities,
                },
                {
                    'label': 'Seuil d\'alerte',
                    'backgroundColor': 'rgba(239, 68, 68, 0.3)',
                    'borderColor': 'rgb(239, 68, 68)',
                    'data': thresholds,
                    'borderDash': [5, 5],
                }
            ]
        })


class SearchView(LoginRequiredMixin, View):
    """Global search view for the dashboard"""
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        
        if not query:
            return render(request, 'dashboard/search.html', {'query': query})
        
        # Search participants
        participants = Participant.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query)
        )[:10]
        
        # Search activities
        activities = Activite.objects.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query)
        )[:10]
        
        # Search staff
        responsables = Responsable.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query)
        )[:5]
        
        animateurs = Animateur.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query)
        )[:5]
        
        # Search infrastructure and materials
        infrastructures = Infrastructure.objects.filter(
            Q(nom__icontains=query) | 
            Q(type__icontains=query)
        )[:5]
        
        materials = Materiel.objects.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query)
        )[:5]
        
        context = {
            'query': query,
            'participants': participants,
            'activities': activities,
            'responsables': responsables,
            'animateurs': animateurs,
            'infrastructures': infrastructures,
            'materials': materials,
            'has_results': any([
                participants.exists(),
                activities.exists(),
                responsables.exists(),
                animateurs.exists(),
                infrastructures.exists(),
                materials.exists()
            ])
        }
        
        return render(request, 'dashboard/search.html', context)
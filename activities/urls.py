from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    # Activity management
    path('', views.ActiviteListView.as_view(), name='list'),
    path('add/', views.ActiviteCreateView.as_view(), name='add'),
    path('<int:pk>/', views.ActiviteDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.ActiviteUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ActiviteDeleteView.as_view(), name='delete'),
    
    # Animateurs and Materiel for Activities
    path('<int:pk>/add-animateur/', views.ActiviteAnimateurCreateView.as_view(), name='add_animateur'),
    path('<int:pk>/add-materiel/', views.ActiviteMaterielCreateView.as_view(), name='add_materiel'),
    path('animateur/<int:pk>/delete/', views.ActiviteAnimateurDeleteView.as_view(), name='delete_animateur'),
    path('materiel/<int:pk>/delete/', views.ActiviteMaterielDeleteView.as_view(), name='delete_materiel'),
    
    # Inscriptions
    path('inscriptions/', views.InscriptionListView.as_view(), name='inscription_list'),
    path('inscriptions/add/', views.InscriptionCreateView.as_view(), name='inscription_add'),
    path('inscriptions/<int:pk>/update/', views.InscriptionUpdateView.as_view(), name='inscription_update'),
    path('inscriptions/<int:pk>/delete/', views.InscriptionDeleteView.as_view(), name='inscription_delete'),
    
    # Quick inscriptions
    path('quick-inscription/', views.QuickInscriptionView.as_view(), name='quick_inscription'),
    path('quick-inscription/participant/<int:participant_id>/', views.QuickInscriptionView.as_view(), name='quick_inscription_participant'),
    path('quick-inscription/activity/<int:activity_id>/', views.QuickInscriptionView.as_view(), name='quick_inscription_activity'),
    
    # Participant activities
    path('participant/<int:pk>/activities/', views.ParticipantActivitiesView.as_view(), name='participant_activities'),
    
    # API
    path('check-capacity/<int:pk>/', views.check_activity_capacity, name='check_capacity'),
]
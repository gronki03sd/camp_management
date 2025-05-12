from django.urls import path
from . import views

app_name = 'participants'

urlpatterns = [
    # Participant management
    path('', views.ParticipantListView.as_view(), name='list'),
    path('add/', views.ParticipantCreateView.as_view(), name='add'),
    path('<int:pk>/', views.ParticipantDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.ParticipantUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ParticipantDeleteView.as_view(), name='delete'),
    
    # Participant files
    path('<int:pk>/add-file/', views.ParticipantFileCreateView.as_view(), name='add_file'),
    path('file/<int:pk>/delete/', views.ParticipantFileDeleteView.as_view(), name='delete_file'),
    
    # API
    path('<int:pk>/activities-json/', views.participant_activities_json, name='activities_json'),
]
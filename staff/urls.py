from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Dashboard and list view
    path('', views.StaffListView.as_view(), name='list'),
    path('dashboard/', views.StaffDashboardView.as_view(), name='dashboard'),
    
    # Responsable management
    path('responsable/<int:pk>/', views.ResponsableDetailView.as_view(), name='responsable_detail'),
    path('responsable/add/', views.ResponsableCreateView.as_view(), name='responsable_add'),
    path('responsable/<int:pk>/update/', views.ResponsableUpdateView.as_view(), name='responsable_update'),
    path('responsable/<int:pk>/delete/', views.ResponsableDeleteView.as_view(), name='responsable_delete'),
    
    # Animateur management
    path('animateur/<int:pk>/', views.AnimateurDetailView.as_view(), name='animateur_detail'),
    path('animateur/add/', views.AnimateurCreateView.as_view(), name='animateur_add'),
    path('animateur/<int:pk>/update/', views.AnimateurUpdateView.as_view(), name='animateur_update'),
    path('animateur/<int:pk>/delete/', views.AnimateurDeleteView.as_view(), name='animateur_delete'),
    
    # Schedule management
    path('<str:staff_type>/<int:pk>/add-schedule/', views.StaffScheduleCreateView.as_view(), name='add_schedule'),
    path('schedule/<int:pk>/delete/', views.StaffScheduleDeleteView.as_view(), name='delete_schedule'),
    
    # API
    path('<str:staff_type>/<int:pk>/activities-json/', views.staff_activities_json, name='activities_json'),
]
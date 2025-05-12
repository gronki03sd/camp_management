from django.urls import path
from . import views

app_name = 'infrastructure'

urlpatterns = [
    # Infrastructure management
    path('', views.InfrastructureListView.as_view(), name='list'),
    path('add/', views.InfrastructureCreateView.as_view(), name='add'),
    path('<int:pk>/', views.InfrastructureDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.InfrastructureUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.InfrastructureDeleteView.as_view(), name='delete'),
    
    # Infrastructure reservations
    path('<int:pk>/reserve/', views.InfrastructureReservationCreateView.as_view(), name='reserve'),
    path('reservation/<int:pk>/delete/', views.InfrastructureReservationDeleteView.as_view(), name='delete_reservation'),
    
    # Material management
    path('materiel/', views.MaterielListView.as_view(), name='materiel_list'),
    path('materiel/add/', views.MaterielCreateView.as_view(), name='materiel_add'),
    path('materiel/<int:pk>/', views.MaterielDetailView.as_view(), name='materiel_detail'),
    path('materiel/<int:pk>/update/', views.MaterielUpdateView.as_view(), name='materiel_update'),
    path('materiel/<int:pk>/delete/', views.MaterielDeleteView.as_view(), name='materiel_delete'),
]
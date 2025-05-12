from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('charts/participants/', views.ParticipantsChartView.as_view(), name='participants_chart'),
    path('charts/activities/', views.ActivitiesChartView.as_view(), name='activities_chart'),
    path('charts/materials/', views.MaterialsChartView.as_view(), name='materials_chart'),
]
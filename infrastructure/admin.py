from django.contrib import admin
from .models import Infrastructure, Materiel, InfrastructureReservation

class InfrastructureReservationInline(admin.TabularInline):
    model = InfrastructureReservation
    extra = 1

@admin.register(Infrastructure)
class InfrastructureAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'capacite', 'localisation', 'disponible')
    list_filter = ('type', 'disponible')
    search_fields = ('nom', 'type', 'localisation')
    list_editable = ['disponible']
    inlines = [InfrastructureReservationInline]
    fieldsets = (
        (None, {
            'fields': ('nom', 'type', 'capacite', 'localisation', 'disponible', 'photo')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Maintenance', {
            'fields': ('maintenance_notes', 'last_maintenance_date', 'next_maintenance_date')
        }),
    )

@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):
    list_display = ('nom', 'quantite_disponible', 'condition', 'date_achat', 'prix_unitaire')
    list_filter = ('condition', 'date_achat')
    search_fields = ('nom', 'description', 'fournisseur')
    list_editable = ['quantite_disponible', 'condition']
    fieldsets = (
        (None, {
            'fields': ('nom', 'description', 'quantite_disponible', 'condition', 'photo')
        }),
        ('Achat', {
            'fields': ('date_achat', 'prix_unitaire', 'fournisseur')
        }),
    )

@admin.register(InfrastructureReservation)
class InfrastructureReservationAdmin(admin.ModelAdmin):
    list_display = ('infrastructure', 'date_debut', 'date_fin', 'responsable', 'motif')
    list_filter = ('date_debut', 'date_fin', 'infrastructure')
    search_fields = ('motif', 'responsable', 'infrastructure__nom')
    date_hierarchy = 'date_debut'
    autocomplete_fields = ['infrastructure']
from django.contrib import admin
from .models import Activite, ActiviteAnimateur, ActiviteMateriel, Inscription

class InscriptionInline(admin.TabularInline):
    model = Inscription
    extra = 1
    autocomplete_fields = ['participant']

class ActiviteAnimateurInline(admin.TabularInline):
    model = ActiviteAnimateur
    extra = 1
    autocomplete_fields = ['animateur']

class ActiviteMaterielInline(admin.TabularInline):
    model = ActiviteMateriel
    extra = 1
    autocomplete_fields = ['materiel']

@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_debut', 'duree', 'responsable', 'capacite_max', 'get_participants_count', 'annulee')
    list_filter = ('date_debut', 'annulee', 'responsable')
    search_fields = ('nom', 'description', 'responsable__nom', 'responsable__prenom')
    date_hierarchy = 'date_debut'
    autocomplete_fields = ['responsable', 'infrastructure']
    inlines = [InscriptionInline, ActiviteAnimateurInline, ActiviteMaterielInline]
    fieldsets = (
        (None, {
            'fields': ('nom', 'description', 'points_cles', 'image')
        }),
        ('Programmation', {
            'fields': ('date_debut', 'duree', 'responsable', 'infrastructure')
        }),
        ('Détails', {
            'fields': ('capacite_max', 'niveau_difficulte', 'age_minimum', 'age_maximum')
        }),
        ('Statut', {
            'fields': ('annulee', 'raison_annulation')
        }),
    )

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('participant', 'activite', 'date_inscription', 'statut', 'a_participe')
    list_filter = ('statut', 'date_inscription', 'a_participe', 'activite')
    search_fields = ('participant__nom', 'participant__prenom', 'activite__nom')
    date_hierarchy = 'date_inscription'
    autocomplete_fields = ['participant', 'activite']
    list_editable = ['statut', 'a_participe']

@admin.register(ActiviteAnimateur)
class ActiviteAnimateurAdmin(admin.ModelAdmin):
    list_display = ('activite', 'animateur', 'role')
    list_filter = ('activite', 'animateur')
    search_fields = ('activite__nom', 'animateur__nom', 'animateur__prenom', 'role')
    autocomplete_fields = ['activite', 'animateur']

@admin.register(ActiviteMateriel)
class ActiviteMaterielAdmin(admin.ModelAdmin):
    list_display = ('activite', 'materiel', 'quantite_requise')
    list_filter = ('activite', 'materiel')
    search_fields = ('activite__nom', 'materiel__nom')
    autocomplete_fields = ['activite', 'materiel']
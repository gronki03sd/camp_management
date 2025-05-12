from django.contrib import admin
from .models import Responsable, Animateur, StaffSchedule

class StaffScheduleInline(admin.TabularInline):
    model = StaffSchedule
    extra = 1
    fk_name = 'responsable'

class AnimateurScheduleInline(admin.TabularInline):
    model = StaffSchedule
    extra = 1
    fk_name = 'animateur'

@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'specialite', 'email', 'telephone', 'is_active')
    list_filter = ('is_active', 'date_embauche', 'specialite')
    search_fields = ('nom', 'prenom', 'email', 'telephone', 'specialite')
    date_hierarchy = 'date_embauche'
    list_editable = ['is_active']
    inlines = [StaffScheduleInline]
    fieldsets = (
        (None, {
            'fields': ('nom', 'prenom', 'specialite', 'photo')
        }),
        ('Informations de contact', {
            'fields': ('telephone', 'email')
        }),
        ('Emploi', {
            'fields': ('date_embauche', 'is_active', 'notes')
        }),
        ('Compte utilisateur', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )
    autocomplete_fields = ['user']

@admin.register(Animateur)
class AnimateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'competence', 'email', 'telephone', 'is_active')
    list_filter = ('is_active', 'date_embauche', 'competence')
    search_fields = ('nom', 'prenom', 'email', 'telephone', 'competence')
    date_hierarchy = 'date_embauche'
    list_editable = ['is_active']
    inlines = [AnimateurScheduleInline]
    fieldsets = (
        (None, {
            'fields': ('nom', 'prenom', 'competence', 'photo')
        }),
        ('Informations de contact', {
            'fields': ('telephone', 'email')
        }),
        ('Emploi', {
            'fields': ('date_embauche', 'is_active', 'notes')
        }),
        ('Compte utilisateur', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )
    autocomplete_fields = ['user']

@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ('get_staff_name', 'date', 'start_time', 'end_time', 'notes')
    list_filter = ('date', 'responsable', 'animateur')
    search_fields = ('responsable__nom', 'responsable__prenom', 'animateur__nom', 'animateur__prenom', 'notes')
    date_hierarchy = 'date'
    autocomplete_fields = ['responsable', 'animateur']

    def get_staff_name(self, obj):
        if obj.responsable:
            return f"Responsable: {obj.responsable.get_full_name()}"
        elif obj.animateur:
            return f"Animateur: {obj.animateur.get_full_name()}"
        return "Non assigné"
    get_staff_name.short_description = 'Membre du personnel'
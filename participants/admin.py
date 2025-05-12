from django.contrib import admin
from .models import Participant, ParticipantFile

class ParticipantFileInline(admin.TabularInline):
    model = ParticipantFile
    extra = 1

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'telephone', 'date_naissance', 'date_inscription', 'get_age')
    list_filter = ('date_inscription', 'has_authorization')
    search_fields = ('nom', 'prenom', 'email', 'telephone')
    date_hierarchy = 'date_inscription'
    ordering = ('nom', 'prenom')
    inlines = [ParticipantFileInline]
    fieldsets = (
        (None, {
            'fields': ('nom', 'prenom', 'date_naissance', 'photo')
        }),
        ('Informations de contact', {
            'fields': ('adresse', 'telephone', 'email')
        }),
        ('Urgence et santé', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'health_notes', 'has_authorization')
        }),
    )

@admin.register(ParticipantFile)
class ParticipantFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'participant', 'file_type', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('title', 'participant__nom', 'participant__prenom')
    date_hierarchy = 'created_at'
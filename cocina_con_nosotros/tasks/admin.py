from django.contrib import admin
from .models import Task, SecuritySettings
from auditlog.models import LogEntry

# Register your models here.
class TaskAdmin(admin.ModelAdmin):
  readonly_fields = ('created', )

admin.site.register(Task, TaskAdmin)

@admin.register(SecuritySettings)
class SecuritySettingsAdmin(admin.ModelAdmin):
    list_display = ['failure_limit']
    list_editable = ['failure_limit']
    list_display_links = None  # Esto permite que todos los campos sean editables directamente
    help_text = "Modifica el límite de intentos fallidos aquí"

#admin.site.register(LogEntry)

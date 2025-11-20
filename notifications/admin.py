from django.contrib import admin
from .models import EmailNotification


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'email_type', 'subject', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'email_type', 'created_at']
    search_fields = ['recipient__username', 'recipient__email', 'subject', 'email_type']
    readonly_fields = ['created_at', 'sent_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Email', {
            'fields': ('recipient', 'email_type', 'subject', 'status')
        }),
        ('Fechas', {
            'fields': ('created_at', 'sent_at')
        }),
        ('Error (si aplica)', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # No permitir crear emails manualmente desde el admin
        return False
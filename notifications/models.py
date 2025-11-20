from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class EmailNotification(models.Model):
    """
    Modelo simple para trackear emails enviados
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_notifications')
    email_type = models.CharField(max_length=50)  # ej: 'solicitud_creada', 'cita_confirmada'
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email_type} → {self.recipient.email} ({self.status})"
    
    def mark_as_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error):
        self.status = 'failed'
        self.error_message = str(error)
        self.save()

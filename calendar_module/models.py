from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()

class CalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('absence', 'Absence'),
        ('block', 'Block'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default='other')
    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"

    @property
    def is_past(self):
        return self.end_datetime < timezone.localtime().date()
    
    

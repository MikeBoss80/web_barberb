from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
    
class FlowType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class FlowStatus(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    type_flow = models.ForeignKey(FlowType, on_delete=models.CASCADE, related_name='status_flows', null=True)
    final = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class FlowInstance(models.Model):
    workflow_type = models.ForeignKey(FlowType, on_delete=models.CASCADE)
    status = models.ForeignKey(FlowStatus, on_delete=models.CASCADE)
    comments = models.TextField(blank=True, null=True)
    recipient = models.ForeignKey(User, related_name='recipient_flows', on_delete=models.SET_NULL, null=True, blank=True) #Persona a quien yo le solicito
    created_by = models.ForeignKey(User, related_name='created_flows', on_delete=models.SET_NULL, null=True, blank=True)#Persona que lo solicita
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(User, related_name='updated_flows', on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    # metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.workflow_type.name} - {self.requester.username} - {self.status.name}"
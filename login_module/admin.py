from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'document', 'establishment', 'data_complete', 'qa_average')
    search_fields = ('user__username', 'document')
    list_filter = ('data_complete',)

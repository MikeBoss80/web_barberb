from django.shortcuts import render
from django.views.generic import TemplateView
from .models import CalendarEvent

class CalendarView(TemplateView):
    template_name = 'calendar_module/calendar_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = CalendarEvent.objects.filter(user=self.request.user, approved=True)
        context['events'] = events
        return context
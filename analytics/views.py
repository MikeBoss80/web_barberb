from django.utils import timezone
from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic import ListView,TemplateView, UpdateView,CreateView,DeleteView
from .services import get_daily_info


class AnalyticsView(TemplateView):
    template_name = 'dashboard.html'
    
    def get_breadcrumb(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_daily_info(self.request))
        return context

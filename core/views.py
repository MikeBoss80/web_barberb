from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.

class HomepageView(TemplateView):
    """Vista principal Main//Home"""
    
    template_name = 'core/main.html'

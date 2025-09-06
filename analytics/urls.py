from django.urls import path
from analytics.views import AnalyticsView

app_name = 'analytics'

urlpatterns = [
    path('', AnalyticsView.as_view(), name='dashboard'),
]   

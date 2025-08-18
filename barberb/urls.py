"""
URL configuration for barberb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.cache import never_cache
from django.views.generic import RedirectView
from decorator_include import decorator_include

decorators = [never_cache]  # Quitamos login_required

urlpatterns = [
    # Redirección de la raíz directamente al login
    path('', RedirectView.as_view(url='/login_module/login/', permanent=False), name='home'),

    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('admin_module/', decorator_include(decorators, ('admin_module.urls', "admin_module"), namespace='admin_module')),
    path('services_module/', decorator_include(decorators, 'services_module.urls')),
    path('login_module/', include('login_module.urls')),
    path('barber_module/', include('barber_module.urls')),  # también sin login_required
]

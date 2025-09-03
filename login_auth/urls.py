# login_auth/urls.py
# -----------------------------------------------------------
# Este archivo centraliza las rutas de autenticación social.
# Se incluye allauth, que ya trae las rutas de login, logout
# y callback para Google u otros proveedores.
# -----------------------------------------------------------

from django.urls import path, include

urlpatterns = [
    # Rutas de django-allauth (login social con Google y otros)
    path("accounts/", include("allauth.urls")),
]

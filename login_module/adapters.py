# login_module/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if hasattr(user, "profile") and not user.profile.data_complete:
            # Redirigir a la vista para completar perfil (sin namespace)
            return reverse("login_module:fill_profile")
        
        # Usar la vista de redirección que valida roles y grupos (sin namespace)
        return reverse('login_module:redirect_after_login')

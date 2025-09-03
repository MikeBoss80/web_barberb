# login_module/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if hasattr(user, "profile") and not user.profile.data_complete:
            # Redirigir a la vista para completar perfil
            return reverse("login_module:fill_profile")      
        # Redirigir al home si ya está completo
        return reverse('admin_module:main') 

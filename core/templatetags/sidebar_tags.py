from django import template

register = template.Library()

@register.simple_tag
def modules_sidebar(user):
    if not user.is_authenticated:
        return []

    if user.is_superuser:
        return [
            # ('admin_dashboard', 'Administrador'),
            # ('usuarios', 'Gestión de usuarios'),
        ]
    elif user.groups.filter(name='Administrador').exists():
        return [
            ('core:test', 'person-circle' , 'Administrador'),
            ('admin_module:barberos', 'person-circle' , 'Barberos'),
        ]
    return [
        ('services_module:services_main', 'globe-americas' , 'Mapa'),
    ]

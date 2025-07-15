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
            ('admin_module:main', 'person-circle' , 'Dashboard'),
            ('admin_module:citas','calendar2-date-fill','Citas'),
            ('admin_module:collabs','people-fill','Colaboradores'),
            ('admin_module:servicios', 'basket', 'Productos'),
            ('admin_module:inventario','receipt-cutoff','Inventario'),
            ('admin_module:admin_solicitudes_list','device-ssd-fill','Solicitudes'),
            ('admin_module:contenidos','shop','Establecimiento'),
            ('admin_module:soporte','info-circle','Soporte'),
        ]
    elif user.groups.filter(name='Barbero').exists():
        return [
            ('admin_module:main', 'person-circle' , 'Dashboard'),
            ('admin_module:citas','calendar2-date-fill','Citas'),
            ('admin_module:admin_solicitudes_list','device-ssd-fill','Solicitudes'),
            ('admin_module:soporte','info-circle','Soporte'),
        ]
    return [
        ('services_module:services_main', 'globe-americas' , 'Reservar'),
        ('admin_module:citas','calendar2-date-fill','Citas'),

    ]

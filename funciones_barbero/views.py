from django.http import HttpResponse

def index(request):
    return HttpResponse("Hola, esta es la app funciones_barbero")
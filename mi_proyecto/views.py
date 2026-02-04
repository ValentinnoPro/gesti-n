from django.shortcuts import render

def index(request):
    """
    Vista para la página de inicio.
    Esta vista renderiza la plantilla 'index.html' y muestra un mensaje de bienvenida.
    """
    return render(request, 'base.html')
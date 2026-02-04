from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente
from django.core.paginator import Paginator
from django.contrib import messages

# Create your views here.


# Funcion que muestra la lista de los clientes.
def lista_clientes(request):
    """
    Vista para mostrar la lista de todos los clientes.
    """
    lista_clientes = Cliente.objects.filter(activo=True).order_by('nombre')
    paginator = Paginator(lista_clientes, 4)  # Mostrar 4 clientes por página.
    num_pagina = request.GET.get('page') or 1  # Obtener el número de página de la solicitud, por defecto es 1
    pagina_actual = paginator.get_page(num_pagina)
    
    return render(request, 'clientes/lista_clientes.html', {'pagina_actual': pagina_actual})


#Funcion que nos permite crear un nuevo cliente.
def crear_cliente(request):
    """
    Vista para crear un nuevo cliente.
    Si el método de la solicitud es POST, se procesan los datos del formulario y 
    se crea un nuevo cliente.
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        
        Cliente.objects.create(nombre=nombre, apellido=apellido, email=email, telefono=telefono)
        
        messages.success(request, "✅ Cliente creado correctamente.")
        return redirect('lista_clientes')
    
    return render(request, 'clientes/crear_cliente.html')


# Funcion que nos permite editar los datos de un cliente.
def editar_cliente(request, cliente_id):
    """
    Vista para editar los datos de un cliente.
    Esta vista permite al usuario editar la información de un cliente existente.
    Si el método de la solicitud es POST, se actualizan los datos del cliente.
    """
    
    cliente = get_object_or_404(Cliente,id=cliente_id)
    
    # Si el usuario envia los datos.
    if request.method == 'POST':
        #Actualizamos los datos del cliente.
        cliente.nombre = request.POST.get('nombre')
        cliente.apellido = request.POST.get('apellido')
        cliente.email = request.POST.get('email')
        cliente.telefono = request.POST.get('telefono')
        # Guardamos los cambios en la base de datos.
        cliente.save()
        
        # Utilizamos messages para mostrar un mensaje de éxito.
        messages.success(request, "✅ Cliente editado correctamente.")
        return redirect('lista_clientes')
    
    # Si el usuario no envia los datos, mostramos el formulario de edición.
    return render(request, 'clientes/editar_cliente.html',{'cliente':cliente} )


def eliminar_cliente(request, cliente_id):
    """
    Vista para eliminar o inactivar un cliente, según si tiene compras.
    Si el cliente tiene compras, se marca como inactivo.
    Si no tiene compras, se elimina de la base de datos.
    """

    cliente = get_object_or_404(Cliente, id=cliente_id)
    tiene_compras = cliente.compras.exists()

    if request.method == 'POST':
        if tiene_compras:
            cliente.activo = False
            cliente.save()
            messages.warning(request, "⚠️ Cliente marcado como inactivo porque tiene compras registradas.")
        else:
            cliente.delete()
            messages.success(request, "✅ Cliente eliminado correctamente.")
        return redirect('lista_clientes')

    return render(request, 'clientes/confirmar_eliminar.html', {
        'cliente': cliente,
        'tiene_compras': tiene_compras
    })
    
def clientes_inactivos(request):
    """
    Vista para mostrar la lista de clientes inactivos.
    """
    lista_clientes_inactivos = Cliente.objects.filter(activo=False).order_by('nombre')
    paginator = Paginator(lista_clientes_inactivos, 4)  # Mostrar 4 clientes por página.
    num_pagina = request.GET.get('page') or 1  # Obtener el número de página de la solicitud, por defecto es 1
    pagina_actual = paginator.get_page(num_pagina)
    
    return render(request, 'clientes/clientes_inactivos.html', {'pagina_actual': pagina_actual})
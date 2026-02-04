from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from django.core.paginator import Paginator
from django.contrib import messages

# Create your views here.
# Funcion que muestra la lista de los productos.
def lista_productos(request):
    """
    Muestra la lista de todos los productos disponibles.
    
    """
    lista_productos = Producto.objects.filter(activo=True).order_by('nombre')
    paginator = Paginator(lista_productos, 4)  # Mostrar 4 productos por página
    num_pagina = request.GET.get('page') or 1  # Obtener el número de página de la solicitud, por defecto es 1
    pagina_actual = paginator.get_page(num_pagina)
    
    return render(request, 'productos/lista_productos.html', {'pagina_actual': pagina_actual})

# Funcion para crear un nuevo producto.
def crear_producto(request):
    """
    Esta función permite crear un nuevo producto.

    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        
        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock
        )
        messages.success(request, "✅ Producto creado correctamente.")
        return redirect('lista_productos')
        
        
    return render(request, 'productos/crear_producto.html')
        
# Funcion para editar un producto .
def editar_producto(request, producto_id):
    """
    Permite editar un producto.

    """
    producto = get_object_or_404(Producto,id=producto_id)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        producto.save()
        
        messages.success(request, "✅ Producto editado correctamente.")
        return redirect('lista_productos')
    
    return render(request, 'productos/editar_producto.html', {'producto': producto})

# Funcion para eliminar un producto.
def eliminar_producto(request, producto_id):
    """
    Permite eliminar un producto.

    """
    producto = get_object_or_404(Producto, id=producto_id)
    se_vendio = producto.detalles_venta.exists()  # Verifica si el producto ha sido vendido
    
    if request.method == 'POST':
        if se_vendio:
            # Si el producto ha sido vendido, lo inactivamos en lugar de eliminarlo.
            producto.activo = False
            producto.save()
            messages.warning(request, "✅ Producto inactivado correctamente.")
        else:
            # Si el producto no ha sido vendido, lo podemos eliminar.
            producto.delete()
            messages.success(request, "✅ Producto eliminado correctamente.")
        return redirect('lista_productos')
    
    
    return render(request, 'productos/eliminar_producto.html', {
        'producto': producto,
        'se_vendio': se_vendio
    })
    
def productos_inactivos(request):
    """
    Muestra la lista de productos inactivos.
    
    """
    lista_productos_inactivos = Producto.objects.filter(activo=False).order_by('nombre')
    paginator = Paginator(lista_productos_inactivos, 4)  # Mostrar 4 productos por página
    num_pagina = request.GET.get('page') or 1  # Obtener el número de página de la solicitud, por defecto es 1
    pagina_actual = paginator.get_page(num_pagina)
    
    return render(request, 'productos/productos_inactivos.html', {'pagina_actual': pagina_actual})
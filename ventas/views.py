from django.shortcuts import render, redirect, get_object_or_404
from .models import Venta, DetallesVenta
from clientes.models import Cliente
from productos.models import Producto
from django.core.paginator import Paginator
from django.contrib import messages

def lista_ventas(request):
    ventas = Venta.objects.filter(anulada = False).order_by('-fecha')  # ordenadas por fecha descendente
    paginator = Paginator(ventas, 2)  # mostrar 4 ventas por página

    page_number = request.GET.get('page') or 1
    pagina_actual = paginator.get_page(page_number)

    return render(request, 'ventas/lista_ventas.html', {
        'pagina_actual': pagina_actual
    })


def crear_venta(request):
    # Obtenemos los parámetros de búsqueda de cliente y producto desde la URL
    cliente_query = request.GET.get('buscar_cliente', '')
    producto_query = request.GET.get('buscar_producto', '')

    # Por defecto, no mostramos clientes ni productos
    clientes = Cliente.objects.none()
    productos = Producto.objects.none()

    # Si hay consultas de búsqueda, filtramos los clientes y productos
    if cliente_query:
        clientes = Cliente.objects.filter(nombre__icontains=cliente_query)
    if producto_query:
        productos = Producto.objects.filter(nombre__icontains=producto_query, stock__gt=0)
        
    # Incializamos variables para almacenar el cliente seleccionado y los productos seleccionados
    cliente_seleccionado = ''
    productos_seleccionados = []

    if request.method == 'POST':
        # Obtener el id del cliente que viene desde el formulario enviado por POST.
        cliente_id = request.POST.get('cliente')
        #Buscamos el cliente en la base de datos, si no lo encuentra, devuelve un 404.
        cliente = get_object_or_404(Cliente, id=cliente_id)

        # Obtenemos los IDs de los productos seleccionados desde el formulario.
        productos_ids = request.POST.getlist('productos')
        
        productos_seleccionados = productos_ids
        cliente_seleccionado = cliente_id

        hay_error = False  # Bandera para controlar errores
        

        # Hacemos una validación de los productos seleccionados
        for prod_id in productos_ids:
            producto = get_object_or_404(Producto, id=prod_id)
            cantidad_str = request.POST.get(f'cantidad_{prod_id}')

            # Si la cantidad no es valida, mostramos un mensaje de error y salimos del bucle.
            try:
                cantidad = int(cantidad_str)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                messages.error(request, "Cantidad inválida.")
                hay_error = True
                break  
            
            # Si la cantidad es valida, verificamos si hay suficiente stock.
            if producto.stock < cantidad:
                messages.error(request, f'Stock insuficiente para el producto {producto.nombre}.')
                hay_error = True
                break

        if not hay_error:
            venta = Venta.objects.create(cliente=cliente)
            for prod_id in productos_ids:
                producto = get_object_or_404(Producto, id=prod_id)
                cantidad = int(request.POST.get(f'cantidad_{prod_id}'))

                DetallesVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )

                producto.stock -= cantidad
                producto.save()

            messages.success(request, "✅ Venta registrada correctamente.")
            return redirect('lista_ventas')

    return render(request, 'ventas/crear_venta.html', {
        'clientes': clientes,
        'productos': productos,
        'cliente_seleccionado': cliente_seleccionado,
        'productos_seleccionados': productos_seleccionados,
        'cliente_query': cliente_query,
        'producto_query': producto_query,
    })


def editar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = venta.detallesventa_set.all()

    cliente_query = request.GET.get('buscar_cliente', '')
    producto_query = request.GET.get('buscar_producto', '')

    cantidades_anteriores = {detalle.producto.id: detalle.cantidad for detalle in detalles}
    cantidades_anteriores_list = list(cantidades_anteriores.items())

    clientes = Cliente.objects.none()
    productos = Producto.objects.none()
    
    
    cliente_seleccionado = ''
    productos_seleccionados = []
    
    if cliente_query:
        clientes = Cliente.objects.filter(nombre__icontains=cliente_query)
    if producto_query:
        productos = Producto.objects.filter(nombre__icontains=producto_query, stock__gt=0)
        
        # Sumamos la cantidad anterior al stock para productos que ya estaban en la venta
        for producto in productos:
            if producto.id in cantidades_anteriores:
                producto.stock += cantidades_anteriores[producto.id]



    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        cliente = get_object_or_404(Cliente, id=cliente_id)

        productos_ids = request.POST.getlist('productos')
        
        productos_seleccionados = productos_ids
        cliente_seleccionado = cliente_id

        hay_error = False

        for prod_id in productos_ids:
            producto = get_object_or_404(Producto, id=prod_id)
            cantidad_str = request.POST.get(f'cantidad_{prod_id}')
            try:
                cantidad = int(cantidad_str)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                messages.error(request, "Cantidad inválida.")
                hay_error = True
                break

            cantidad_anterior = cantidades_anteriores.get(producto.id, 0)
            stock_disponible = producto.stock + cantidad_anterior

            if stock_disponible < cantidad:
                messages.error(request, f'Stock insuficiente para el producto {producto.nombre}. Stock disponible: {stock_disponible}.')
                hay_error = True
                break

        if not hay_error:
            venta.cliente = cliente
            venta.save()
            venta.detallesventa_set.all().delete()

            for prod_id in productos_ids:
                producto = get_object_or_404(Producto, id=prod_id)
                cantidad = int(request.POST.get(f'cantidad_{prod_id}'))

                DetallesVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )

                cantidad_anterior = cantidades_anteriores.get(producto.id, 0)
                stock_actual = producto.stock + cantidad_anterior
                producto.stock = stock_actual - cantidad
                producto.save()

            messages.success(request, "✅ Venta actualizada correctamente.")
            return redirect('lista_ventas')

    return render(request, 'ventas/formulario_venta.html', {
        'venta': venta,
        'clientes': clientes,
        'productos': productos,
        'cliente_seleccionado': cliente_seleccionado,
        'productos_seleccionados': productos_seleccionados,
        'cantidades_anteriores_list': cantidades_anteriores_list,
        'cliente_query': cliente_query,
        'producto_query': producto_query,
    })


    
    
def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    
    if request.method == 'POST':
        venta.anulada = True
        venta.save()
        
        messages.success(request, " Venta marcada como inactiva.")
        return redirect('lista_ventas')

    return render(request, 'ventas/eliminar_venta.html', {'venta': venta})

def ventas_anuladas(request):
    ventas = Venta.objects.filter(anulada=True).order_by('-fecha')
    paginator = Paginator(ventas, 2)  # mostrar 4 ventas por página

    page_number = request.GET.get('page') or 1
    pagina_actual = paginator.get_page(page_number)

    return render(request, 'ventas/ventas_anuladas.html', {
        'pagina_actual': pagina_actual
    })
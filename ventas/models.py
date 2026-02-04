from django.db import models
from clientes.models import Cliente  
from productos.models import Producto  

# Create your models here.

# Modelo para representar la venta
class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='compras')  # Relación con el cliente
    productos = models.ManyToManyField(Producto, through= 'DetallesVenta')  # Relación con los productos vendidos
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha de la venta
    anulada = models.BooleanField(default=False)  # Indica si la venta ha sido anulada
    
    @property
    def calcular_total(self):
        return sum(detalle.subtotal for detalle in self.detallesventa_set.all())

    def __str__(self):
        cliente_str = f"{self.cliente.nombre} {self.cliente.apellido}" 
        return f"Venta {self.id} - {cliente_str} - Fecha: {self.fecha} - Total: ${self.calcular_total:.2f}."

    
# Modelo para representar los detalles de la venta
class DetallesVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)  # Relación con la venta
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta')  # Relación con el producto
    cantidad = models.PositiveIntegerField()  # Cantidad del producto vendido
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Precio unitario del producto

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario  # Método para calcular el subtotal de la venta
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}. ${self.precio_unitario} c.u. = ${self.subtotal}."
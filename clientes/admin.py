from django.contrib import admin
from .models import Cliente

# Register your models here.
# Mostrar el modelo Cliente en el panel de administración.
admin.site.register(Cliente)
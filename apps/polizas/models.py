from django.db import models
from apps.core.models import BaseModel
from django.conf import settings


class Aseguradora(BaseModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Ramo(BaseModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class FormaPago(BaseModel):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Contratante(BaseModel):
    nombre = models.CharField(max_length=200)
    # MODIFICACIÓN CLAVE: Añadir unique=True para evitar duplicados en la BD
    documento = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Asegurado(BaseModel):
    nombre = models.CharField(max_length=200)
    # MODIFICACIÓN CLAVE: Añadir unique=True para evitar duplicados en la BD
    documento = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class ReporteGenerado(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    parametros = models.JSONField()  # Almacena los parámetros de búsqueda
    archivo_path = models.CharField(max_length=255)
    tipo_reporte = models.CharField(max_length=50)

    def __str__(self):
        return f"Reporte {self.id} - {self.usuario.username}"


class Poliza(BaseModel):
    aseguradora = models.ForeignKey(Aseguradora, on_delete=models.PROTECT)
    ramo = models.ForeignKey(Ramo, on_delete=models.PROTECT)
    forma_pago = models.ForeignKey(FormaPago, on_delete=models.PROTECT)
    numero = models.CharField(max_length=50, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    vigencia = models.CharField(max_length=50)
    prima_total = models.DecimalField(max_digits=10, decimal_places=2)
    monto_asegurado = models.DecimalField(max_digits=10, decimal_places=2)
    i_trimestre = models.DecimalField(max_digits=10, decimal_places=2)
    ii_trimestre = models.DecimalField(max_digits=10, decimal_places=2)
    iii_trimestre = models.DecimalField(max_digits=10, decimal_places=2)
    iv_trimestre = models.DecimalField(max_digits=10, decimal_places=2)
    renovacion = models.CharField(max_length=100)
    contratante = models.ForeignKey(Contratante, on_delete=models.PROTECT)
    asegurado = models.ForeignKey(Asegurado, on_delete=models.PROTECT)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='polizas_creadas')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                        related_name='polizas_actualizadas', null=True)

    def __str__(self):
        return f"{self.numero} - {self.aseguradora.nombre}"



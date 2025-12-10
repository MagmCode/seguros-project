from django.contrib import admin
from .models import Poliza, Aseguradora, Ramo, Contratante, Asegurado, FormaPago, ReporteGenerado

@admin.register(Aseguradora)
class AseguradoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Ramo)
class RamoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(FormaPago)
class FormaPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')

# --- IMPORTANTE: ESTO PERMITE VER Y BORRAR CONTRATANTES DUPLICADOS ---
@admin.register(Contratante)
class ContratanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'documento', 'email', 'telefono')
    search_fields = ('nombre', 'documento')

@admin.register(Asegurado)
class AseguradoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'documento', 'email', 'telefono')
    search_fields = ('nombre', 'documento')

@admin.register(Poliza)
class PolizaAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'aseguradora', 'contratante', 'fecha_inicio', 'fecha_fin', 'prima_total')
    list_filter = ('aseguradora', 'ramo', 'forma_pago', 'fecha_inicio')
    search_fields = ('numero', 'contratante__nombre', 'asegurado__nombre')
    autocomplete_fields = ['aseguradora', 'ramo', 'contratante', 'asegurado']

@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo_reporte', 'fecha_generacion')
    list_filter = ('tipo_reporte', 'fecha_generacion')
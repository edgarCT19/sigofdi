from django.views.decorators.cache import never_cache
from django.shortcuts import render

from system.decorators import login_required_custom
from system.models import Area, Edificio, FacturaEnergeticaTriple, FacturaPdbt, InventarioClimatizacion, InventarioLuminarias, InventarioMiscelaneos, PeriodoInventario, Subestacion, UnidadResponsable

# Vistas para el inicio del administrador del sistema
@never_cache
@login_required_custom
def Inicio(request):
    """
    Vista para el inicio del administrador del sistema.
    Muestra un resumen de las estadísticas clave del sistema.
    - Restringida a usuarios autenticados con el decorador login_required_custom.
    - never_cache: evita el almacenamiento en caché de esta vista.
    - Muestra conteos de unidades responsables, edificios, subestaciones, facturas, áreas y equipos de inventario.
    """
    context = {
        "total_unidades": UnidadResponsable.objects.count(),
        "total_edificios": Edificio.objects.count(),
        "total_subestaciones": Subestacion.objects.count(),
        "total_facturas": FacturaEnergeticaTriple.objects.count() + FacturaPdbt.objects.count(),
        "total_areas": Area.objects.count(),
        "total_climatizacion": InventarioClimatizacion.objects.count(),
        "total_luminarias": InventarioLuminarias.objects.count(),
        "total_miscelaneos": InventarioMiscelaneos.objects.count(),
        "periodos": PeriodoInventario.objects.order_by('-fecha_inicio')[:5],  # últimos 5 periodos
        # Puedes agregar más como consumos promedio o más detallado
    }
    return render(request, 'systemsigo/index.html', context)
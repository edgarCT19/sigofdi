from datetime import datetime

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from system.models import InventarioClimatizacion
from system.views import get_user
from system.decorators import login_required_custom

from mongoengine.errors import DoesNotExist

@never_cache
@login_required_custom
def historial_climatizacion_admin(request):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect("login")

    registros_baja = InventarioClimatizacion.objects(activo=False).order_by('-fecha_baja')

    return render(request, 'systemsigo/Inventarios/Climatizacion/registros_eliminados.html', {
        'registros': registros_baja
    })  

@never_cache
@login_required_custom
def dar_baja_inventario_climatizacion(request, his_id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect("login")

    try:
        his = InventarioClimatizacion.objects.get(id=his_id)
    except DoesNotExist:
        messages.error(request, "Inventario no encontrado.")
        return redirect('listado_inventario_climatizacion')

    his.activo = False
    his.fecha_baja = datetime.now()
    his.dado_baja_por = user
    his.save()

    messages.success(request, "Registro dado de baja correctamente.")
    return redirect('listado_inventario_climatizacion')

@never_cache
@login_required_custom
def registro_climatizacion_bajas_admin(request):
    """
    Vista para listar los inventarios dados de baja (activo=False)
    """
    registros_baja = InventarioClimatizacion.objects(activo=False).order_by('-fecha_baja')
    
    return render(request, 'systemsigo/Inventarios/Climatizacion/registros_eliminados.html', {
        'registros': registros_baja
    })


@never_cache
@login_required_custom
def restaurar_registro_climatizacion(request, registro_id):
    """
    Función para reactivar un inventario previamente dado de baja
    """
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect("login")

    try:
        registro = InventarioClimatizacion.objects.get(id=registro_id)
    except DoesNotExist:
        messages.error(request, "Registro no encontrado.")
        return redirect('historial_climatizacion_admin')

    registro.activo = True
    registro.fecha_reactivacion = datetime.now()
    registro.reactivado_por = user
    registro.save()

    messages.success(request, "Registro restaurado correctamente.")
    return redirect('historial_climatizacion_admin')
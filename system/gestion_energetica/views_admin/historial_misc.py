from datetime import datetime

from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.utils.timezone import now

from system.models import InventarioMiscelaneos, Usuario
from system.views import get_user
from system.decorators import login_required_custom

from mongoengine.errors import DoesNotExist

@never_cache
@login_required_custom
def historial_miscelaneos_admin(request):
    registros_inactivos = InventarioMiscelaneos.objects.filter(activo=False)
    return render(request, 'systemsigo/Inventarios/Miscelaneos/registros_eliminados.html', {
        "miscelaneos_inactivos": registros_inactivos
    })

@never_cache
@login_required_custom
def dar_baja_miscelaneo_admin(request, id):
    if request.method == "POST":
        try:
            miscelaneo = InventarioMiscelaneos.objects.get(id=id)
            miscelaneo.activo = False
            miscelaneo.fecha_baja = now()
            if request.user.is_authenticated:
                usuario = Usuario.objects.get(id=request.user.id)
                miscelaneo.dado_baja_por = usuario
            miscelaneo.save()
            messages.success(request, "Registro dado de baja correctamente.")
            return JsonResponse({"success": True})
        except InventarioMiscelaneos.DoesNotExist:
            return JsonResponse({"success": False, "error": "El registro no existe."})
    return JsonResponse({"success": False, "error": "Método no permitido."})

@never_cache
@login_required_custom
def restaurar_miscelaneo_admin(request, id):
    if request.method == "POST":
        try:
            miscelaneo = InventarioMiscelaneos.objects.get(id=id)
            miscelaneo.activo = True
            miscelaneo.fecha_reactivacion = now()
            if request.user.is_authenticated:
                usuario = Usuario.objects.get(id=request.user.id)
                miscelaneo.reactivado_por = usuario
            miscelaneo.save()
            messages.success(request, "Registro restaurado correctamente.")
            return JsonResponse({"success": True})
        except InventarioMiscelaneos.DoesNotExist:
            return JsonResponse({"success": False, "error": "El registro no existe."})
    return JsonResponse({"success": False, "error": "Método no permitido."})
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now

from system.models import InventarioLuminarias, Usuario
from system.views import get_user

# Historial de luminarias dadas de baja
def historial_luminarias_admin(request):
    luminarias_inactivas = InventarioLuminarias.objects(activo=False)
    return render(request, "systemsigo/Inventarios/Luminarias/registros_eliminados.html", {
        "luminarias_inactivas": luminarias_inactivas
    })


# Dar de baja una luminaria
def dar_baja_luminaria(request, id):
    try:
        luminaria = InventarioLuminarias.objects.get(id=id)
        luminaria.activo = False
        luminaria.fecha_baja = now()

        if request.user.is_authenticated:
            usuario = Usuario.objects.get(id=request.user.id)
            luminaria.dado_baja_por = usuario

        luminaria.save()
        messages.success(request, "Registro dado de baja correctamente.")
    except InventarioLuminarias.DoesNotExist:
        messages.error(request, "La luminaria no existe.")
    return redirect("listado_inventario_luminarias")


# Reactivar una luminaria
def restaurar_registro_luminaria(request, id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect("login")

    if request.method == "POST":
        try:
            luminaria = InventarioLuminarias.objects.get(id=id)
            luminaria.activo = True
            luminaria.fecha_reactivacion = now()
            luminaria.dado_baja_por = user
            luminaria.save()

            if request.user.is_authenticated:
                usuario = Usuario.objects.get(id=request.user.id)
                luminaria.reactivado_por = usuario

            luminaria.save()
            messages.success(request, "Registro restaurado correctamente.")
            return JsonResponse({"success": True})
        except InventarioLuminarias.DoesNotExist:
            return JsonResponse({"success": False, "error": "La luminaria no existe."})
    return JsonResponse({"success": False, "error": "Método no permitido"})
   
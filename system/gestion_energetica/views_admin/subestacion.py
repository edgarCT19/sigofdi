from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib import messages

from system.models import Subestacion, UnidadResponsable, Tarifas
from system.decorators import login_required_custom
from system.views import get_user
from system.gestion_energetica.views_admin.utils import is_admin
from system.decorators import login_required_custom

from datetime import datetime


# Desarrollar el crud de subestaciones con filtro por unidad responsable

@never_cache
@login_required_custom
def subestaciones_admin(request):
    """
    Vista para administrar subestaciones con filtrado por unidad responsable.

    - Si se proporciona un parámetro 'ur' en la URL, filtra las subestaciones por la unidad responsable correspondiente.
    - Si no se proporciona, muestra todas las subestaciones.
    - También pasa todas las unidades responsables al contexto para permitir la selección en la interfaz.
    - La vista está protegida por autenticación y no se almacena en caché. 
    """

    ur_id = request.GET.get('ur')  # ID de la unidad responsable seleccionada

    unidades_responsables = UnidadResponsable.objects()  # Todas las UR

    if ur_id:
        subestaciones = Subestacion.objects(unidad_responsable=ur_id)
    else:
        subestaciones = Subestacion.objects()

    context = {
        'subestaciones': subestaciones,
        'unidades_responsables': unidades_responsables,
        'ur_filtrada': ur_id,
    }

    return render(request, 'systemsigo/Subestaciones/subestaciones_admin.html', context)

@never_cache
@login_required_custom
def registrar_subestacion_admin(request):
    """
    Vista para crear una nueva subestación.

    - Renderiza un formulario para ingresar los detalles de la subestación.
    - La vista está protegida por autenticación y no se almacena en caché.
    """

    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')
    
    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            no_servicio = request.POST.get("no_servicio")
            no_medidor = request.POST.get("no_medidor")
            tarifa = request.POST.get("tarifa")
            multiplicador = request.POST.get("multiplicador")

            unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)

            subestacion = Subestacion(
                unidad_responsable=unidad_responsable,
                no_servicio=no_servicio,
                no_medidor=no_medidor,
                tarifa=tarifa,
                multiplicador= multiplicador,
            )
            subestacion.save()

            messages.success(request, "Subestación creada correctamente")
            return redirect("admin_subestaciones")

        except Exception as e:
            messages.error(request, f"Error al crear la subestación: {str(e)}")

    unidades_responsables = UnidadResponsable.objects()  # Todas las UR

    context = {
        'unidades_responsables': unidades_responsables,
    }

    return render(request, 'systemsigo/Subestaciones/add_form.html', context)

@never_cache
@login_required_custom
def editar_subestacion_admin(request, id):
    """
    Vista para editar una subestación existente.

    - Renderiza un formulario con los detalles actuales de la subestación para su edición.
    - La vista está protegida por autenticación y no se almacena en caché.
    """

    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    subestacion = Subestacion.objects.get(id=id)

    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            subestacion.unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)
            subestacion.no_servicio = request.POST.get("no_servicio")
            subestacion.no_medidor = request.POST.get("no_medidor")
            subestacion.tarifa = request.POST.get("tarifa")
            subestacion.multiplicador = request.POST.get("multiplicador")

            subestacion.save()

            messages.success(request, "Subestación actualizada correctamente")
            return redirect("admin_subestaciones")

        except Exception as e:
            messages.error(request, f"Error al actualizar la subestación: {str(e)}")

    unidades_responsables = UnidadResponsable.objects()  # Todas las UR

    context = {
        'subestacion': subestacion,
        'unidades_responsables': unidades_responsables,
    }

    return render(request, 'systemsigo/Subestaciones/edit_form.html', context)

@never_cache
@login_required_custom
def eliminar_subestacion_admin(request, id):
    """
    Vista para eliminar una subestación existente.

    - La vista está protegida por autenticación y no se almacena en caché.
    """

    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    try:
        subestacion = Subestacion.objects.get(id=id)
        subestacion.delete()
        messages.success(request, "Subestación eliminada correctamente")
    except Exception as e:
        messages.error(request, f"Error al eliminar la subestación: {str(e)}")

    return redirect("admin_subestaciones")
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import never_cache

from datetime import datetime

from django.http import Http404

from system.models import AlmacenamientoTemporal, UnidadResponsable, Usuario
from system.decorators import login_required_custom
from system.views import get_user
from system.gestion_energetica.views_admin.utils import is_admin


@never_cache
@login_required_custom
def almacenamiento_temporal_lista_admin(request):
    almacenamientos = AlmacenamientoTemporal.objects.all()
    return render(request, 'systemsigo_ambiental/Almacenamiento_temp/lista_bit_almacenamiento.html', {
        'almacenamientos': almacenamientos
    })


@never_cache
@login_required_custom
def almacenamiento_temporal_crear_admin(request):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            centro_acopio = request.POST.get("centro_acopio")
            tipo_residuo = request.POST.get("tipo_residuo")
            cantidad = request.POST.get("cantidad")
            estado_fisico = request.POST.get("estado_fisico")
            creti = request.POST.get("creti")
            tipo_envase = request.POST.get("tipo_envase")
            capacidad_medida = request.POST.get("capacidad_medida")

            unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)

            almacenamiento = AlmacenamientoTemporal(
                unidad_responsable=unidad_responsable,
                centro_acopio=centro_acopio,
                tipo_residuo=tipo_residuo,
                cantidad=cantidad,
                estado_fisico=estado_fisico,
                creti=creti,
                tipo_envase=tipo_envase,
                capacidad_medida=capacidad_medida,
                creado_por=user
            )
            almacenamiento.save()

            messages.success(request, "Registro de almacenamiento creado correctamente")
            return redirect("almacenamiento_temporal")

        except Exception as e:
            messages.error(request, f"Error al crear: {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Almacenamiento_temp/add_form.html', {
        'urs': urs
    })


@never_cache
@login_required_custom
def almacenamiento_temporal_editar_admin(request, id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    try:
        almacenamiento = AlmacenamientoTemporal.objects.get(id=id)
    except AlmacenamientoTemporal.DoesNotExist:
        raise Http404("Registro no encontrado")

    if request.method == "POST":
        almacenamiento.unidad_responsable = UnidadResponsable.objects.get(id=request.POST.get("unidad_responsable"))
        almacenamiento.centro_acopio = request.POST.get("centro_acopio")
        almacenamiento.tipo_residuo = request.POST.get("tipo_residuo")
        almacenamiento.cantidad = request.POST.get("cantidad")
        almacenamiento.estado_fisico = request.POST.get("estado_fisico")
        almacenamiento.creti = request.POST.get("creti")
        almacenamiento.tipo_envase = request.POST.get("tipo_envase")
        almacenamiento.capacidad_medida = request.POST.get("capacidad_medida")
        almacenamiento.actualizado_por = user
        almacenamiento.ultima_actualizacion = datetime.now()
        almacenamiento.save()

        messages.success(request, "Registro actualizado correctamente")
        return redirect("almacenamiento_temporal")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Almacenamiento_temp/edit_form.html', {
        'almacenamiento': almacenamiento,
        'urs': urs
    })


@never_cache
@login_required_custom
def almacenamiento_temporal_eliminar_admin(request, id):
    try:
        almacenamiento = AlmacenamientoTemporal.objects.get(id=id)
        almacenamiento.delete()
        messages.success(request, "Registro eliminado correctamente")
    except AlmacenamientoTemporal.DoesNotExist:
        raise Http404("Registro no encontrado")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {str(e)}")

    return redirect("almacenamiento_temporal")
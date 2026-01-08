from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import never_cache

from datetime import datetime

from system.models import BitacoraMensual, UnidadResponsable, Usuario
from system.views import get_user
from system.gestion_energetica.views_admin.utils import is_admin
from system.decorators import login_required_custom

@never_cache
@login_required_custom
def bitacora_mensual_lista_admin(request):
    bitacoras = BitacoraMensual.objects.all()
    return render(request, 'systemsigo_ambiental/Bitacora_mensual/lista_bit_mensual.html', {
        'bitacoras': bitacoras
    })


@never_cache
@login_required_custom
def bitacora_mensual_crear_admin(request):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            laboratorio = request.POST.get("laboratorio")
            tipo_residuo = request.POST.get("tipo_residuo")
            cantidad = request.POST.get("cantidad")
            estado_fisico = request.POST.get("estado_fisico")
            creti = request.POST.get("creti")
            tipo_envase = request.POST.get("tipo_envase")
            capacidad_medida = request.POST.get("capacidad_medida")

            unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)

            bitacora = BitacoraMensual(
                unidad_responsable=unidad_responsable,
                laboratorio=laboratorio,
                tipo_residuo=tipo_residuo,
                cantidad=cantidad,
                estado_fisico=estado_fisico,
                creti=creti,
                tipo_envase=tipo_envase,
                capacidad_medida=capacidad_medida,
                creado_por=user
            )
            bitacora.save()

            messages.success(request, "Bitácora creada correctamente ")
            return redirect("bitacora_mensual_lista_admin")

        except Exception as e:
            messages.error(request, f"Error al crear la bitácora : {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Bitacora_mensual/add_form.html', {
        'urs': urs
    })


@never_cache
@login_required_custom
def bitacora_mensual_editar_admin(request, id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    bitacora = BitacoraMensual.objects.get(id=id)

    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            bitacora.unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)
            bitacora.laboratorio = request.POST.get("laboratorio")
            bitacora.tipo_residuo = request.POST.get("tipo_residuo")
            bitacora.cantidad = request.POST.get("cantidad")
            bitacora.estado_fisico = request.POST.get("estado_fisico")
            bitacora.creti = request.POST.get("creti")
            bitacora.tipo_envase = request.POST.get("tipo_envase")
            bitacora.capacidad_medida = request.POST.get("capacidad_medida")
            bitacora.actualizado_por = user
            bitacora.ultima_actualizacion = datetime.now()
            bitacora.save()

            messages.success(request, "Bitácora actualizada correctamente ")
            return redirect("bitacora_mensual_lista_admin")

        except Exception as e:
            messages.error(request, f"Error al actualizar : {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Bitacora_mensual/edit_form.html', {
        'bitacora': bitacora,
        'urs': urs
    })


@never_cache
@login_required_custom
def bitacora_mensual_eliminar_admin(request, id):
    try:
        bitacora = BitacoraMensual.objects.get(id=id)
        bitacora.delete()
        messages.success(request, "Bitácora eliminada correctamente ")
    except Exception as e:
        messages.error(request, f"Error al eliminar : {str(e)}")

    return redirect("bitacora_mensual_lista_admin")
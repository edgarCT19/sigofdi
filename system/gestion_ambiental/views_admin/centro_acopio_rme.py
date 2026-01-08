from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from datetime import datetime
from django.http import Http404

from system.models import CentroAcopioRME, UnidadResponsable, Usuario, Campus
from system.decorators import login_required_custom
from system.views import get_user
from system.gestion_energetica.views_admin.utils import is_admin


@never_cache
@login_required_custom
def centro_de_acopio_rme_admin(request):
    acopios = CentroAcopioRME.objects.all()
    return render(request, 'systemsigo_ambiental/Acopio_rme/lista_acopio_rme.html', {
        'acopios': acopios
    })


@never_cache
@login_required_custom
def centro_acopio_rme_crear_admin(request):
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

            unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)

            acopio = CentroAcopioRME(
                unidad_responsable=unidad_responsable,
                centro_acopio=centro_acopio,
                tipo_residuo=tipo_residuo,
                cantidad=cantidad,
                estado_fisico=estado_fisico,
                creado_por=user
            )
            acopio.save()

            messages.success(request, "Registro de centro de acopio creado correctamente")
            return redirect("centro_acopio_rme_admin")

        except Exception as e:
            messages.error(request, f"Error al crear: {str(e)}")

    urs = UnidadResponsable.objects.all()
    campus = Campus.objects.all()
    return render(request, 'systemsigo_ambiental/Acopio_rme/add_form.html', {
        'urs': urs,
        'campus': campus
    })


@never_cache
@login_required_custom
def centro_acopio_rme_editar_admin(request, id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    try:
        acopio = CentroAcopioRME.objects.get(id=id)
    except CentroAcopioRME.DoesNotExist:
        raise Http404("Registro no encontrado")

    if request.method == "POST":
        acopio.unidad_responsable = UnidadResponsable.objects.get(id=request.POST.get("unidad_responsable"))
        acopio.centro_acopio = request.POST.get("centro_acopio")
        acopio.tipo_residuo = request.POST.get("tipo_residuo")
        acopio.cantidad = request.POST.get("cantidad")
        acopio.estado_fisico = request.POST.get("estado_fisico")
        acopio.actualizado_por = user
        acopio.ultima_actualizacion = datetime.now()
        acopio.save()

        messages.success(request, "Registro actualizado correctamente")
        return redirect("centro_acopio_rme_admin")

    urs = UnidadResponsable.objects.all()
    campus = Campus.objects.all()
    return render(request, 'systemsigo_ambiental/Acopio_rme/edit_form.html', {
        'acopio': acopio,
        'urs': urs,
        'campus': campus
    })


@never_cache
@login_required_custom
def centro_acopio_rme_eliminar_admin(request, id):
    try:
        acopio = CentroAcopioRME.objects.get(id=id)
        acopio.delete()
        messages.success(request, "Registro eliminado correctamente")
    except CentroAcopioRME.DoesNotExist:
        raise Http404("Registro no encontrado")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {str(e)}")

    return redirect("centro_acopio_rme_admin")
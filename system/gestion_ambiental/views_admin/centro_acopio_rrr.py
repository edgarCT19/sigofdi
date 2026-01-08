from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import Http404

from datetime import datetime

from system.models import CentroAcopioRRR, UnidadResponsable, Usuario
from system.decorators import login_required_custom
from system.views import get_user
from system.gestion_energetica.views_admin.utils import is_admin


@never_cache
@login_required_custom
def centro_de_acopio_rrr_admin(request):
    acopio = CentroAcopioRRR.objects.all()
    return render(request, 'systemsigo_ambiental/Acopio_rrr/lista_acopio_rrr.html', {
        'acopio': acopio
    })


@never_cache
@login_required_custom
def centro_acopio_rrr_crear_admin(request):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            centro_acopio = request.POST.get("centro_acopio")
            dependencia = request.POST.get("dependencia")
            pet = request.POST.get("pet")
            papel = request.POST.get("papel")
            carton = request.POST.get("carton")
            metales = request.POST.get("metales")

            unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)

            registro = CentroAcopioRRR(
                unidad_responsable=unidad_responsable,
                centro_acopio=centro_acopio,
                dependencia=dependencia,
                pet=pet,
                papel=papel,
                carton=carton,
                metales=metales,
                creado_por=user
            )
            registro.save()

            messages.success(request, "Registro creado correctamente")
            return redirect("centro_acopio_rrr_admin")

        except Exception as e:
            messages.error(request, f"Error al crear: {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Acopio_rrr/add_form.html', {
        'urs': urs
    })


@never_cache
@login_required_custom
def centro_acopio_rrr_editar_admin(request, id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    try:
        acopio = CentroAcopioRRR.objects.get(id=id)
    except CentroAcopioRRR.DoesNotExist:
        raise Http404("Registro no encontrado")

    if request.method == "POST":
        try:
            acopio.unidad_responsable = UnidadResponsable.objects.get(id=request.POST.get("unidad_responsable"))
            acopio.centro_acopio = request.POST.get("centro_acopio")
            acopio.dependencia = request.POST.get("dependencia")
            acopio.pet = request.POST.get("pet")
            acopio.papel = request.POST.get("papel")
            acopio.carton = request.POST.get("carton")
            acopio.metales = request.POST.get("metales")
            acopio.actualizado_por = user
            acopio.ultima_actualizacion = datetime.now()
            acopio.save()

            messages.success(request, "Registro actualizado correctamente")
            return redirect("centro_acopio_rrr_admin")

        except Exception as e:
            messages.error(request, f"Error al actualizar: {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Acopio_rrr/edit_form.html', {
        'acopio': acopio,
        'urs': urs
    })


@never_cache
@login_required_custom
def centro_acopio_rrr_eliminar_admin(request, id):
    try:
        registro = CentroAcopioRRR.objects.get(id=id)
        registro.delete()
        messages.success(request, "Registro eliminado correctamente")
    except CentroAcopioRRR.DoesNotExist:
        raise Http404("Registro no encontrado")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {str(e)}")

    return redirect("centro_acopio_rrr_admin")
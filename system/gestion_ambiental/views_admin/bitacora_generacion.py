from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from datetime import datetime
from django.http import Http404

from system.models import BitacoraGeneracionRPBI, UnidadResponsable, Usuario
from system.decorators import login_required_custom
from system.views import get_user
from system.gestion_energetica.views_admin.utils import is_admin

@never_cache
@login_required_custom
def bitacora_generacion_rpbi(request):
    bitacoras = BitacoraGeneracionRPBI.objects.all()
    return render(request, 'systemsigo_ambiental/Bitacora_generacion/lista_rpbi_generacion.html', {
        'bitacoras': bitacoras
    })    

@never_cache
@login_required_custom
def bitacora_rpbi_crear_admin(request):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            area_dependencia = request.POST.get("area_dependencia")
            cultivos_cepas = request.POST.get("cultivos_cepas")
            punzocortantes = request.POST.get("punzocortantes")
            patologicos = request.POST.get("patologicos")
            no_anatomicos = request.POST.get("no_anatomicos")
            sangre = request.POST.get("sangre")

            unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)

            bitacora = BitacoraGeneracionRPBI(
                unidad_responsable=unidad_responsable,
                area_dependencia=area_dependencia,
                cultivos_cepas=cultivos_cepas,
                punzocortantes=punzocortantes,
                patologicos=patologicos,
                no_anatomicos=no_anatomicos,
                sangre=sangre,
                creado_por=user
            )
            bitacora.save()

            messages.success(request, "Bitácora RPBI creada correctamente")
            return redirect("bitacora_generacion_rpbi")

        except Exception as e:
            messages.error(request, f"Error al crear la bitácora: {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Bitacora_generacion/add_form.html', {
        'urs': urs
    })


@never_cache
@login_required_custom
def bitacora_rpbi_editar_admin(request, id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    try:
        bitacora = BitacoraGeneracionRPBI.objects.get(id=id)
    except BitacoraGeneracionRPBI.DoesNotExist:
        raise Http404("Registro no encontrado")

    if request.method == "POST":
        try:
            bitacora.unidad_responsable = UnidadResponsable.objects.get(id=request.POST.get("unidad_responsable"))
            bitacora.area_dependencia = request.POST.get("area_dependencia")
            bitacora.cultivos_cepas = request.POST.get("cultivos_cepas")
            bitacora.punzocortantes = request.POST.get("punzocortantes")
            bitacora.patologicos = request.POST.get("patologicos")
            bitacora.no_anatomicos = request.POST.get("no_anatomicos")
            bitacora.sangre = request.POST.get("sangre")
            bitacora.actualizado_por = user
            bitacora.ultima_actualizacion = datetime.now()
            bitacora.save()

            messages.success(request, "Bitácora RPBI actualizada correctamente")
            return redirect("bitacora_generacion_rpbi")

        except Exception as e:
            messages.error(request, f"Error al actualizar: {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Bitacora_generacion/edit_form.html', {
        'bitacora': bitacora,
        'urs': urs
    })


@never_cache
@login_required_custom
def bitacora_rpbi_eliminar_admin(request, id):
    try:
        bitacora = BitacoraGeneracionRPBI.objects.get(id=id)
        bitacora.delete()
        messages.success(request, "Bitácora RPBI eliminada correctamente")
    except BitacoraGeneracionRPBI.DoesNotExist:
        raise Http404("Registro no encontrado")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {str(e)}")

    return redirect("bitacora_generacion_rpbi")
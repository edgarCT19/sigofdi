from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import Http404
from datetime import datetime

from system.models import VertederoMunicipal, UnidadResponsable, Usuario
from system.decorators import login_required_custom
from system.views import get_user
from system.gestion_energetica.views_admin.utils import is_admin


@never_cache
@login_required_custom
def vertedero_municipal_admin(request):
    """Lista todos los registros de Vertedero Municipal"""
    vertederos = VertederoMunicipal.objects.all()
    return render(request, 'systemsigo_ambiental/Vertedero_municipal/lista_bit_vertedero.html', {
        'vertederos': vertederos
    })


@never_cache
@login_required_custom
def vertedero_municipal_crear_admin(request):
    """Crear un nuevo registro de Vertedero Municipal"""
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            dependencia = request.POST.get("dependencia")
            tipo_desecho = request.POST.get("tipo_desecho")
            capacidad = request.POST.get("capacidad")

            unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)

            vertedero = VertederoMunicipal(
                unidad_responsable=unidad_responsable,
                dependencia=dependencia,
                tipo_desecho=tipo_desecho,
                capacidad=capacidad,
                creado_por=user
            )
            vertedero.save()

            messages.success(request, "Registro en Vertedero Municipal creado correctamente")
            return redirect("vertedero_municipal_admin")

        except Exception as e:
            messages.error(request, f"Error al crear: {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Vertedero_municipal/add_form.html', {
        'urs': urs
    })


@never_cache
@login_required_custom
def vertedero_municipal_editar_admin(request, id):
    """Editar un registro de Vertedero Municipal"""
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    try:
        vertedero = VertederoMunicipal.objects.get(id=id)
    except VertederoMunicipal.DoesNotExist:
        raise Http404("Registro no encontrado")

    if request.method == "POST":
        vertedero.unidad_responsable = UnidadResponsable.objects.get(id=request.POST.get("unidad_responsable"))
        vertedero.dependencia = request.POST.get("dependencia")
        vertedero.tipo_desecho = request.POST.get("tipo_desecho")
        vertedero.capacidad = request.POST.get("capacidad")
        vertedero.actualizado_por = user
        vertedero.ultima_actualizacion = datetime.now()
        vertedero.save()

        messages.success(request, "Registro actualizado correctamente")
        return redirect("vertedero_municipal_admin")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo_ambiental/Vertedero_municipal/edit_form.html', {
        'vertedero': vertedero,
        'urs': urs
    })


@never_cache
@login_required_custom
def vertedero_municipal_eliminar_admin(request, id):
    """Eliminar un registro de Vertedero Municipal (borrado físico)"""
    try:
        vertedero = VertederoMunicipal.objects.get(id=id)
        vertedero.delete()
        messages.success(request, "Registro eliminado correctamente")
    except VertederoMunicipal.DoesNotExist:
        raise Http404("Registro no encontrado")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {str(e)}")

    return redirect("vertedero_municipal_admin")
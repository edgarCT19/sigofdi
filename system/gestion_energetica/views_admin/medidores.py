from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from datetime import datetime

from system.models import Medidores, UnidadResponsable
from system.views import get_user
from system.gestion_energetica.views_admin.utils import is_admin
from system.decorators import login_required_custom

@never_cache
@login_required_custom
def medidores_lista_admin(request):
    medidores = Medidores.objects.all()
    return render(request, 'systemsigo/Medidores/medidores.html', {
        'medidores': medidores
    })

@never_cache
@login_required_custom
def medidores_crear_admin(request):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            no_medidor = request.POST.get("no_medidor")
            capacidad_transformador = request.POST.get("capacidad_transformador")

            unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)

            medidor = Medidores(
                unidad_responsable=unidad_responsable,
                no_medidor=no_medidor,
                capacidad_transformador=capacidad_transformador,
                creado_por=user
            )
            medidor.save()

            messages.success(request, "Medidor creado correctamente")
            return redirect("medidores")

        except Exception as e:
            messages.error(request, f"Error al crear el medidor: {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo/Medidores/add_form.html', {
        'urs': urs
    })

@never_cache
@login_required_custom
def medidores_editar_admin(request, id):
    user = get_user(request)
    if not user or not is_admin(user):
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    medidor = Medidores.objects.get(id=id)

    if request.method == "POST":
        try:
            unidad_responsable_id = request.POST.get("unidad_responsable")
            medidor.unidad_responsable = UnidadResponsable.objects.get(id=unidad_responsable_id)
            medidor.no_medidor = request.POST.get("no_medidor")
            medidor.capacidad_transformador = request.POST.get("capacidad_transformador")
            medidor.actualizado_por = user
            medidor.ultima_actualizacion = datetime.now()
            medidor.save()

            messages.success(request, "Medidor actualizado correctamente")
            return redirect("medidores")

        except Exception as e:
            messages.error(request, f"Error al actualizar el medidor: {str(e)}")

    urs = UnidadResponsable.objects.all()
    return render(request, 'systemsigo/Medidores/edit_form.html', {
        'medidor': medidor,
        'urs': urs
    })

@never_cache
@login_required_custom
def medidores_eliminar_admin(request, id):
    try:
        medidor = Medidores.objects.get(id=id)
        medidor.delete()
        messages.success(request, "Medidor eliminado correctamente")
    except Exception as e:
        messages.error(request, f"Error al eliminar el medidor: {str(e)}")

    return redirect("medidores")
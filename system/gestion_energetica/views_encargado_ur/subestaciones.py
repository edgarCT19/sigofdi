from decimal import Decimal

from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect, render

from system.decorators import login_required_custom
from system.models import Subestacion, UnidadResponsable
from system.views import get_user

@never_cache
@login_required_custom
def listar_subestaciones_encargado(request):
    """
    Vista para listar las subestaciones del encargado de unidad responsable (UR).

    - Esta vista obtiene todas las subestaciones asociadas a la unidad responsable del usuario y extrae las tarifas disponibles.    
    - Si el usuario no es un encargado de UR, se redirige a la página de inicio con un mensaje de error.
    - Los registros de subestaciones y tarifas disponibles se pasan al contexto para ser renderizados en la plantilla correspondiente.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    urs = user.unidad_responsable if user.unidad_responsable else []
    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    # Extraer tarifas disponibles según sus subestaciones
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)
    return render(request, 'Encargado_UR/Subestaciones/subestaciones.html', {
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles
    })

@never_cache
@login_required_custom
def registrar_subestacion(request):
    """
    Vista para registrar una nueva subestación por parte del encargado de unidad responsable (UR). 

    - Esta vista permite al encargado de UR registrar una nueva subestación asociada a su unidad responsable.
    - Si el usuario no es un encargado de UR, se redirige a la página de inicio con un mensaje de error.
    - Se valida que todos los campos requeridos estén completos y se maneja cualquier error durante el registro.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    urs = user.unidad_responsable if user.unidad_responsable else []
    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    if user.rol != 'encargado_ur':
        messages.error(request, "No tienes permiso para registrar servicios.")
        return redirect('encargado_ur')

    if request.method == 'POST':
        no_servicio = request.POST.get('no_servicio')
        no_medidor = request.POST.get('no_medidor')
        tarifa = request.POST.get('tarifa')
        multiplicador = request.POST.get('multiplicador')
        ur_id = request.POST.get('unidad_responsable')

        if not (no_servicio and no_medidor and tarifa and multiplicador and ur_id):
            messages.error(request, "Todos los campos son obligatorios.")
        else:
            try:
                ur = UnidadResponsable.objects.get(id=ur_id)

                if ur not in urs:
                    messages.error(request, "No puedes usar esa unidad responsable.")
                    return redirect('registrar_subestacion')

                sub = Subestacion(
                    unidad_responsable=ur,
                    no_servicio=int(no_servicio),
                    no_medidor=no_medidor,
                    tarifa=tarifa,
                    multiplicador=Decimal(multiplicador)
                )
                sub.save()

                messages.success(request, "Servicio registrado exitosamente.")
                return redirect('listar_subestaciones_encargado')

            except Exception as e:
                messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'Encargado_UR/Subestaciones/add_form.html', {
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles,
        'urs': urs
    })

@never_cache
@login_required_custom
def editar_subestacion(request, id):
    """
    Vista para editar una subestación del encargado de unidad responsable (UR). 

    - Esta vista permite al encargado de UR editar los detalles de una subestación específica asociada a su unidad responsable.
    - Si el usuario no es un encargado de UR, se redirige a la página de inicio con un mensaje de error.
    - Se valida que todos los campos requeridos estén completos y se maneja cualquier error durante la actualización.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    urs = user.unidad_responsable if user.unidad_responsable else []
    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    if user.rol != 'encargado_ur':
        return redirect('encargado_ur')

    try:
        sub = subestaciones.get(id=id)
    except Subestacion.DoesNotExist:
        messages.error(request, "Servicio no encontrado.")
        return redirect('listar_subestaciones_encargado')

    if request.method == 'POST':
        try:
            ur_id = request.POST.get('unidad_responsable')
            ur = UnidadResponsable.objects.get(id=ur_id)

            if ur not in urs:
                messages.error(request, "No puedes usar esa unidad responsable.")
                return redirect('listar_subestaciones_encargado')

            sub.unidad_responsable = ur
            sub.no_servicio = int(request.POST.get('no_servicio'))
            sub.no_medidor = request.POST.get('no_medidor')
            sub.tarifa = request.POST.get('tarifa')
            sub.multiplicador = Decimal(request.POST.get('multiplicador'))
            sub.save()

            messages.success(request, "Servicio actualizado correctamente.")
            return redirect('listar_subestaciones_encargado')

        except ValueError:
            messages.error(request, "Campos numéricos inválidos.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'Encargado_UR/Subestaciones/edit_form.html', {
        'subestacion': sub,
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles,
        'urs': urs
    })

@never_cache
@login_required_custom
def eliminar_subestacion(request, id):
    """
    Vista para eliminar una subestación del encargado de unidad responsable (UR).   
    
    - Esta vista permite al encargado de UR eliminar una subestación específica asociada a su unidad responsable.
    - Si el usuario no es un encargado de UR, se redirige a la página de inicio con un mensaje de error.
    - Se maneja la excepción si la subestación no existe.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    if user.rol != 'encargado_ur':
        return redirect('encargado_ur')

    try:
        urs = user.unidad_responsable if user.unidad_responsable else []
        subestaciones = Subestacion.objects(unidad_responsable__in=urs)
        sub = subestaciones.get(id=id)
        sub.delete()
        messages.success(request, "Subestación eliminada correctamente.")
    except Subestacion.DoesNotExist:
        messages.error(request, "No se encontró la subestación.")
    
    return redirect('listar_subestaciones_encargado')
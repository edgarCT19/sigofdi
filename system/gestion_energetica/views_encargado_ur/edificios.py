from mongoengine.errors import DoesNotExist

from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from system.decorators import login_required_custom
from system.models import Edificio, Subestacion, UnidadResponsable
from system.views import get_user

def get_user_urs(user):
    return user.unidades_responsables if user.unidades_responsables else []

@never_cache
@login_required_custom
def listar_edificios(request):
    """
    Listar edificios de la unidad responsable del usuario.

    - Verifica que el usuario esté autenticado.
    - Obtiene los edificios y subestaciones asociados a la unidad responsable del usuario.
    - Renderiza la plantilla con la lista de edificios y subestaciones.
    - Muestra las tarifas disponibles de las subestaciones.
    - Maneja errores de sesión expirada.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    urs = user.unidad_responsable if user.unidad_responsable else []

    ur_id = request.GET.get('ur')

    edificios = Edificio.objects(unidad_responsable__in=urs)

    if ur_id:
        edificios = edificios.filter(unidad_responsable=ur_id)

    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    return render(
        request,
        'Encargado_UR/Edificios/edificios.html',
        {
            'edificios': edificios,
            'urs': urs,
            'ur_seleccionada': ur_id,
            'subestaciones': subestaciones,
            'tarifas_disponibles': tarifas_disponibles,
        }
    )

@never_cache
@login_required_custom
def alta_edificio(request):
    """ 
    Registrar un nuevo edificio.

    - Verifica que el usuario esté autenticado.
    - Obtiene el nombre del edificio del formulario.
    - Crea un nuevo edificio con el nombre y la unidad responsable del usuario.
    - Muestra un mensaje de éxito si el edificio se registra correctamente.
    - Renderiza el formulario para registrar un edificio.
    - Muestra las subestaciones y tarifas disponibles de la unidad responsable del usuario.
    """
    user = get_user(request)

    # URs que puede gestionar
    urs = user.unidad_responsable if user.unidad_responsable else []

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        ur_id = request.POST.get('unidad_responsable')

        if not nombre or not ur_id:
            messages.error(request, "Nombre y UR son obligatorios.")
            return redirect('alta_edificio')

        # validar que la UR pertenece al usuario
        ur = UnidadResponsable.objects(id=ur_id, id__in=[u.id for u in urs]).first()

        if not ur:
            messages.error(request, "UR no válida.")
            return redirect('alta_edificio')

        Edificio(
            nombre=nombre,
            responsable_alta=user.nombres,
            unidad_responsable=ur
        ).save()

        messages.success(request, "Edificio registrado exitosamente.")
        return redirect('lista_edificios')

    # datos auxiliares
    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    return render(request, 'Encargado_UR/Edificios/add_form.html', {
        'urs': urs,   # enviar URs al template
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles
    })

@never_cache
@login_required_custom
def editar_edificio(request, edificio_id):
    """ 
    Editar un edificio existente.

    - Verifica que el usuario esté autenticado.     
    - Obtiene el edificio por su ID.
    - Actualiza el nombre del edificio con los datos del formulario.
    - Muestra un mensaje de éxito si la actualización es exitosa.
    - Renderiza el formulario de edición con los datos del edificio y las subestaciones disponibles.
    """

    user = get_user(request)
    urs = user.unidad_responsable if user.unidad_responsable else []

    try:
        edificio = Edificio.objects.get(id=edificio_id)
    except DoesNotExist:
        raise Http404("Edificio no encontrado.")

    # seguridad — solo si pertenece a sus UR
    if edificio.unidad_responsable not in urs:
        messages.error(request, "No tienes permiso para editar este edificio.")
        return redirect('lista_edificios')

    if request.method == 'POST':
        edificio.nombre = request.POST.get('nombre')

        ur_id = request.POST.get('unidad_responsable')
        ur = UnidadResponsable.objects(
            id=ur_id,
            id__in=[u.id for u in urs]
        ).first()

        if not ur:
            messages.error(request, "UR no válida.")
            return redirect('lista_edificios')

        edificio.unidad_responsable = ur
        edificio.save()

        messages.success(request, 'Edificio actualizado correctamente.')
        return redirect('lista_edificios')

    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    return render(request, 'Encargado_UR/Edificios/edit_form.html', {
        'edificio': edificio,
        'urs': urs,
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles
    })

@never_cache
@login_required_custom
def eliminar_edificio(request, edificio_id):
    """ 
    Eliminar un edificio existente.

    - Verifica que el usuario esté autenticado.
    - Obtiene el edificio por su ID.
    - Elimina el edificio y muestra un mensaje de éxito.
    - Redirige a la lista de edificios.
    """
    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    if user.rol != 'encargado_ur':
        return redirect('inicio')

    try:
        urs = user.unidad_responsable if user.unidad_responsable else []
        edificio = Edificio.objects(unidad_responsable__in=urs).get(id=edificio_id)
        edificio.delete()
        messages.success(request, "Edificio eliminado correctamente.")
    except DoesNotExist:
        raise Http404("Edificio no encontrado.")
    
    return redirect('lista_edificios')
from datetime import datetime
from urllib import request

from bson import ObjectId
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.decorators.cache import never_cache

from system.decorators import login_required_custom
from system.models import Area, Edificio, Subestacion
from system.views import get_user

def get_user_urs(user):
    return user.unidades_responsables if user.unidades_responsables else []

@never_cache
@login_required_custom
def lista_areas(request):
    """ 
    Lista todas las áreas de la unidad responsable del usuario. 

    - Muestra las áreas junto con sus edificios y subestaciones asociadas.
    - Si el usuario no tiene una sesión válida, redirige al login.
    - Si no hay áreas, muestra un mensaje informativo.
    - También obtiene las tarifas disponibles de las subestaciones asociadas a la unidad responsable.
    - Si ocurre un error al obtener las áreas, muestra un mensaje de error.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    urs = user.unidad_responsable if user.unidad_responsable else []

    # UR seleccionada desde el frontend
    ur_id = request.GET.get('ur')

    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    # Filtro base (seguridad)
    areas = Area.objects(unidad_responsable__in=urs)

    # Filtro adicional por UR seleccionada
    if ur_id:
        areas = areas.filter(unidad_responsable=ur_id)

    return render(
        request,
        'Encargado_UR/Areas/areas.html',
        {
            'areas': areas,
            'urs': urs,
            'ur_seleccionada': ur_id,
            'subestaciones': subestaciones,
            'tarifas_disponibles': tarifas_disponibles
        }
    )

@never_cache
@login_required_custom
def agregar_areas(request):
    """ 
    Agrega una nueva área a la unidad responsable del usuario.

    - Requiere que el usuario esté autenticado.
    - Obtiene la unidad responsable del usuario y los edificios asociados.          
    - Permite al usuario ingresar el nombre del área, edificio, teléfono, cargo, grado de estudio y responsable.
    - Si se envía el formulario, valida los datos y crea una nueva área.
    - Si el área se crea correctamente, redirige a la lista de áreas con un mensaje de éxito.
    - Si hay algún error, muestra un mensaje de error.
    - También obtiene las subestaciones y tarifas disponibles asociadas a la unidad responsable.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    urs = user.unidad_responsable if user.unidad_responsable else []

    edificios = Edificio.objects(unidad_responsable__in=urs)
    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        edificio_id = request.POST.get('edificio')
        telefono = request.POST.get('telefono')
        cargo = request.POST.get('cargo')
        grado_estudio = request.POST.get('grado_estudio')
        responsable = request.POST.get('responsable')

        if not (nombre and edificio_id and responsable):
            messages.error(request, 'Faltan datos obligatorios.')
            return render(request, 'Encargado_UR/Areas/add_form.html', {
                'edificios': edificios,
                'subestaciones': subestaciones,
                'tarifas_disponibles': tarifas_disponibles
            })

        try:
            edificio = Edificio.objects.get(id=edificio_id)
        except Edificio.DoesNotExist:
            messages.error(request, "Edificio inválido.")
            return redirect('lista_areas')

        if edificio.unidad_responsable not in urs:
            messages.error(request, "No tienes permiso para ese edificio.")
            return redirect('lista_areas')

        Area(
            nombre=nombre,
            unidad_responsable=edificio.unidad_responsable,
            edificio=edificio,
            fecha_registro=datetime.now(),
            responsable=responsable,
            telefono=telefono,
            cargo=cargo,
            grado_estudio=grado_estudio
        ).save()

        messages.success(request, 'Área registrada correctamente.')
        return redirect('lista_areas')

    return render(request, 'Encargado_UR/Areas/add_form.html', {
        'edificios': edificios,
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles
    })

@never_cache
@login_required_custom
def editar_areas(request, area_id):
    """ 
    Edita un área existente de la unidad responsable del usuario.

    - Requiere que el usuario esté autenticado.     
    - Obtiene el área a editar por su ID.
    - Verifica  que el área pertenece a la unidad responsable del usuario.  
    - Si el área no existe, muestra un mensaje de error y redirige a la lista de áreas.
    - Si el usuario no tiene permiso para editar el área, redirige a la lista de áreas.
    - Permite al usuario editar el nombre del área, edificio, teléfono, cargo, grado de estudio y responsable.
    - Si se envía el formulario, actualiza el área y redirige a la lista de áreas con un mensaje de éxito.
    - Si hay algún error, muestra un mensaje de error.
    - También obtiene los edificios, subestaciones y tarifas disponibles asociadas a la unidad responsable.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    urs = user.unidad_responsable if user.unidad_responsable else []

    try:
        area = Area.objects.get(id=area_id)
    except Area.DoesNotExist:
        messages.error(request, "Área no encontrada.")
        return redirect('lista_areas')

    if area.unidad_responsable not in urs:
        messages.error(request, "No tienes permiso para editar esta área.")
        return redirect('lista_areas')

    edificios = Edificio.objects(unidad_responsable__in=urs)
    subestaciones = Subestacion.objects(unidad_responsable__in=urs)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    if request.method == 'POST':

        area.nombre = request.POST.get('nombre')
        area.telefono = request.POST.get('telefono')
        area.cargo = request.POST.get('cargo')
        area.grado_estudio = request.POST.get('grado_estudio')
        area.responsable = request.POST.get('responsable')

        edificio_id = request.POST.get('edificio')

        if not edificio_id:
            messages.error(request, "Debe seleccionar un edificio.")
            return render(request, 'Encargado_UR/Areas/edit_form.html', {
                'area': area,
                'edificios': edificios,
                'subestaciones': subestaciones,
                'tarifas_disponibles': tarifas_disponibles
            })

        try:
            edificio = Edificio.objects.get(id=edificio_id)
        except Edificio.DoesNotExist:
            messages.error(request, "Edificio inválido.")
            return redirect('lista_areas')

        if edificio.unidad_responsable not in urs:
            messages.error(request, "No tienes permiso para ese edificio.")
            return redirect('lista_areas')

        area.edificio = edificio
        area.unidad_responsable = edificio.unidad_responsable

        area.save()

        messages.success(request, 'Área actualizada correctamente.')
        return redirect('lista_areas')

    return render(request, 'Encargado_UR/Areas/edit_form.html', {
        'area': area,
        'edificios': edificios,
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles
    })

@never_cache
@login_required_custom
def eliminar_areas(request, area_id):
    """
    Elimina un área de la unidad responsable del usuario.  
             
    - Requiere que el usuario esté autenticado.
    - Obtiene el área a eliminar por su ID.
    - Verifica que el área pertenece a la unidad responsable del usuario.
    - Si el área no existe, muestra un mensaje de error y redirige a la lista de áreas.
    - Si el usuario no tiene permiso para eliminar el área, redirige a la lista de áreas.
    - Si el área se elimina correctamente, muestra un mensaje de éxito y redirige a la lista de áreas.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    urs = user.unidad_responsable if user.unidad_responsable else []

    try:
        area = Area.objects.get(id=area_id)
    except Area.DoesNotExist:
        messages.error(request, "Área no encontrada.")
        return redirect('lista_areas')

    if area.unidad_responsable not in urs:
        messages.error(request, "No tienes permiso para eliminar esta área.")
        return redirect('lista_areas')

    area.delete()
    messages.success(request, "Área eliminada correctamente.")
    return redirect('lista_areas')
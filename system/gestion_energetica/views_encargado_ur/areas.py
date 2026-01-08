from datetime import datetime

from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.decorators.cache import never_cache

from system.decorators import login_required_custom
from system.models import Area, Edificio, Subestacion
from system.views import get_user

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
    
    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    areas = Area.objects(unidad_responsable=user.unidad_responsable)
    return render(request, 'Encargado_UR/Areas/areas.html', {
        'areas': areas,
        'subestaciones': subestaciones,
        'tarifas_disponibles': tarifas_disponibles
    })

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

    unidad = user.unidad_responsable
    edificios = Edificio.objects(unidad_responsable=unidad)
    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        edificio_id = request.POST.get('edificio')
        telefono = request.POST.get('telefono')
        cargo = request.POST.get('cargo')
        grado_estudio = request.POST.get('grado_estudio')
        responsable = request.POST.get('responsable')  # <- Ingresado manualmente

        if nombre and edificio_id and responsable:
            edificio = Edificio.objects.get(id=edificio_id)
            Area(
                nombre=nombre,
                unidad_responsable=unidad,
                edificio=edificio,
                fecha_registro=datetime.now(),
                responsable=responsable,
                telefono=telefono,
                cargo=cargo,
                grado_estudio=grado_estudio
            ).save()
            messages.success(request, 'Área registrada correctamente.')
            return redirect('lista_areas')
        else:
            messages.error(request, 'Faltan datos obligatorios.')

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

    try:
        area = Area.objects.get(id=area_id)
    except Area.DoesNotExist:
        messages.error(request, "Área no encontrada.")
        return redirect('lista_areas')

    if area.unidad_responsable != user.unidad_responsable:
        return redirect('lista_areas')

    edificios = Edificio.objects(unidad_responsable=user.unidad_responsable)
    subestaciones = Subestacion.objects(unidad_responsable=user.unidad_responsable)
    tarifas_disponibles = set(sub.tarifa for sub in subestaciones)

    if request.method == 'POST':
        area.nombre = request.POST.get('nombre')
        edificio_id = request.POST.get('edificio')
        area.telefono = request.POST.get('telefono')
        area.cargo = request.POST.get('cargo')
        area.grado_estudio = request.POST.get('grado_estudio')
        area.responsable = request.POST.get('responsable')  # <- editable manual

        if edificio_id:
            area.edificio = Edificio.objects.get(id=edificio_id)
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

    try:
        area = Area.objects.get(id=area_id)
    except Area.DoesNotExist:
        messages.error(request, "Área no encontrada.")
        return redirect('lista_areas')

    if area.unidad_responsable != user.unidad_responsable:
        messages.error(request, "No tienes permiso para eliminar esta área.")
        return redirect('lista_areas')

    area.delete()
    messages.success(request, "Área eliminada correctamente.")
    return redirect('lista_areas')
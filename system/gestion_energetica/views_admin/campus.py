from bson import ObjectId

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from mongoengine.errors import DoesNotExist

from system.decorators import login_required_custom
from system.models import Campus
from system.forms import CampusForm


@never_cache
@login_required_custom
def listar_campus(request):
    """
    Vista para listar todos los campus registrados en el sistema.
    - Restringida a usuarios autenticados con el decorador login_required_custom.
    - never_cache: evita el almacenamiento en caché de esta vista.
    """
    campus_list = Campus.objects.all()
    return render(request, 'systemsigo/Campus/listar.html', {'campus_list': campus_list})


@never_cache
@login_required_custom
def crear_campus(request):
    """
    Vista para crear un nuevo campus.
    - Muestra un formulario vacío si el método es GET.
    - Si el método es POST y el formulario es válido, guarda el nuevo campus en la base de datos.
    - Muestra mensaje de éxito y redirige a la lista de campus.
    """
    if request.method == 'POST':
        form = CampusForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            campus = Campus(**data)
            campus.save()
            messages.success(request, "¡Campus creado exitosamente!")
            return redirect('listar_campus')
    else:
        form = CampusForm()

    return render(request, 'systemsigo/Campus/add_form.html', {'form': form})


@never_cache
@login_required_custom
def editar_campus(request, campus_id):
    """
    Vista para editar un campus existente.
    - Recupera el campus por su ID.
    - Si el método es POST y el formulario es válido, actualiza los campos.
    - Si es GET, precarga los datos actuales en el formulario.
    """
    campus = Campus.objects.get(id=campus_id)

    if request.method == 'POST':
        form = CampusForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            campus.nomenclatura = data['nomenclatura']
            campus.ubicacion = data['ubicacion']
            campus.metros_cuadrados = data['metros_cuadrados']
            campus.save()
            messages.success(request, "¡Campus actualizado exitosamente!")
            return redirect('listar_campus')
    else:
        form = CampusForm(initial={
            'nomenclatura': campus.nomenclatura,
            'ubicacion': campus.ubicacion,
            'metros_cuadrados': campus.metros_cuadrados,
        })

    return render(request, 'systemsigo/Campus/edit_form.html', {'form': form})


@never_cache
@login_required_custom
@csrf_exempt
def eliminar_campus(request, campus_id):
    """
    Vista para eliminar un campus.
    - Solo acepta peticiones POST.
    - Convierte el campus_id a ObjectId (MongoDB) antes de buscar.
    - Devuelve respuesta JSON con el resultado de la operación.
    - Maneja errores de objeto no encontrado o excepciones genéricas.
    """
    try:
        if request.method == 'POST':
            # Convertir el campus_id a ObjectId para asegurar compatibilidad con MongoEngine
            campus_id = ObjectId(campus_id)
            campus = Campus.objects.get(id=campus_id)
            campus.delete()
            return JsonResponse({'success': True})

        return JsonResponse(
            {'success': False, 'message': 'Método no permitido'},
            status=405
        )

    except DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Campus no encontrado'}, status=404)
    except Exception as e:
        # Captura cualquier error inesperado y lo retorna como mensaje
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
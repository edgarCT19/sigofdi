from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from system.forms import UnidadResponsableForm
from system.models import Campus, UnidadResponsable
from system.decorators import login_required_custom

#Vistas de CRUD's de Unidades Responsables
@never_cache
@login_required_custom
def listar_unidades(request):
    """Lista todas las Unidades Responsables."""

    unidades = UnidadResponsable.objects.all()
    return render(request, 'systemsigo/UR/listar_UR.html', {'unidades': unidades})

@never_cache
@login_required_custom
def crear_unidad(request):
    """Crea una nueva Unidad Responsable."""
    
    if request.method == 'POST':
        form = UnidadResponsableForm(request.POST)
        if form.is_valid():
            campus_id = form.cleaned_data['campus']
            campus = Campus.objects.get(id=campus_id)
            unidad = UnidadResponsable(
                nombre=form.cleaned_data['nombre'],
                total_personas=form.cleaned_data['total_personas'],
                campus=campus
            )
            unidad.save()
            messages.success(request, "Unidad Responsable creada correctamente.")
            return redirect('listar_unidades')
    else:
        form = UnidadResponsableForm()
    return render(request, 'systemsigo/UR/add_form.html', {'form': form})

@never_cache
@login_required_custom
def editar_unidad(request, unidad_id):
    """Edita una Unidad Responsable existente."""

    unidad = UnidadResponsable.objects.get(id=unidad_id)

    if request.method == 'POST':
        form = UnidadResponsableForm(request.POST)
        if form.is_valid():
            unidad.nombre = form.cleaned_data['nombre']
            unidad.total_personas = form.cleaned_data['total_personas']
            campus_id = form.cleaned_data['campus']
            campus = Campus.objects.get(id=campus_id)  # Convertir string a documento
            unidad.campus = campus  # Ahora sí es un documento válido
            unidad.save()
            messages.success(request, "Unidad Responsable actualizada correctamente.")
            return redirect('listar_unidades')
    else:
        form = UnidadResponsableForm(initial={
            'nombre': unidad.nombre,
            'total_personas': unidad.total_personas,
            'campus': str(unidad.campus.id)  # Asegurar que el valor inicial sea un string
        })

    return render(request, 'systemsigo/UR/edit_form.html', {'form': form, 'unidad': unidad})

@never_cache
@login_required_custom
def eliminar_unidad(request, unidad_id):
    """Elimina una Unidad Responsable."""

    if request.method == 'POST':
        try:
            unidad = UnidadResponsable.objects.get(id=unidad_id)
            unidad.delete()
            return JsonResponse({'success': True})
        except UnidadResponsable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Unidad Responsable no encontrada'}, status=404)
    return JsonResponse({'success': False}, status=400)
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from mongoengine.errors import DoesNotExist

from system.models import Tarifas
from system.forms import TarifasForm
from system.decorators import login_required_custom

# Vistas de CRUD's de Tarifas
@never_cache
@login_required_custom
def crear_tarifa(request):
    """Vista para crear una nueva tarifa."""

    if request.method == 'POST':
        form = TarifasForm(request.POST)
        if form.is_valid():
            tarifa = Tarifas(
                nombre=form.cleaned_data['nombre'],
                descripcion=form.cleaned_data['descripcion'],
                tarifa=form.cleaned_data['tarifa']
            )
            tarifa.save()
            messages.success(request, 'La tarifa fue creada correctamente.')
            return redirect('lista_tarifas')
    else:
        form = TarifasForm()
    return render(request, 'systemsigo/Tarifas/add_form.html', {'form': form})

@never_cache
@login_required_custom
def editar_tarifa(request, tarifa_id):
    """Vista para editar una tarifa existente."""

    tarifa = Tarifas.objects.get(id=tarifa_id)

    if request.method == 'POST':
        form = TarifasForm(request.POST)
        if form.is_valid():
            tarifa.nombre = form.cleaned_data['nombre']
            tarifa.descripcion = form.cleaned_data['descripcion']
            tarifa.tarifa = form.cleaned_data['tarifa']
            tarifa.save()
            messages.success(request, 'La tarifa fue actualizada correctamente.')
            return redirect('lista_tarifas')
    else:
        form = TarifasForm(initial={
            'nombre': tarifa.nombre,
            'descripcion': tarifa.descripcion,
            'tarifa': tarifa.tarifa
        })

    return render(request, 'systemsigo/Tarifas/editar_tarifa.html', {'form': form, 'tarifa': tarifa})

@never_cache
@login_required_custom
def eliminar_tarifa(request, id):
    """Vista para eliminar una tarifa existente."""

    if request.method == 'POST':
        try:
            tarifa = Tarifas.objects.get(id=id)
            tarifa.delete()
            return JsonResponse({'success': True})
        except DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Tarifa no encontrada.'})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido.'})

@never_cache
@login_required_custom
def lista_tarifas(request):
    """Vista para listar todas las tarifas."""
    
    tarifas = Tarifas.objects.all()
    return render(request, 'systemsigo/Tarifas/listar_tarifas.html', {'tarifas': tarifas})
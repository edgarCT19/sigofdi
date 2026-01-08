from datetime import datetime

from decimal import Decimal

from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect

from system.models import NIVELES, Area, Edificio, InventarioLuminarias, PeriodoInventario
from system.decorators import login_required_custom
from system.views import get_user

# Vistas de funciones de inventario energetico de luminarias
@never_cache
@login_required_custom
def registrar_inventario_luminarias(request):
    """
    Registrar un nuevo inventario de luminarias.

    - Verifica que el usuario esté logueado y tenga una sesión activa.
    - Obtiene el usuario logueado y su unidad responsable.
    - Obtiene los edificios y niveles disponibles para la unidad responsable.
    - Filtra las áreas según el edificio seleccionado.
    - Procesa el formulario de registro de inventario.
    - Calcula potencia total y consumo mensual.
    - Guarda el inventario y redirige a la lista de inventarios.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    # Obtener periodo activo
    periodo_activo = PeriodoInventario.objects(status="Activo").first()
    if not periodo_activo:
        messages.error(request, "No hay un periodo de inventario activo.")
        return redirect('listar_inventario_luminarias')

    edificios = Edificio.objects(unidad_responsable=user.unidad_responsable)
    niveles = NIVELES
    
    # Persistencia de selecciones
    edificio_id = request.GET.get('edificio') or request.session.get('edificio_lum')
    nivel_sel  = request.GET.get('nivel')   or request.session.get('nivel_lum')
    request.session['edificio_lum'] = edificio_id
    request.session['nivel_lum']    = nivel_sel

    areas_filtradas = Area.objects(edificio=edificio_id) if edificio_id else []

    if request.method == 'POST':
        try:
            edificio = Edificio.objects.get(id=request.POST['edificio'])
            area     = Area.objects.get(id=request.POST['area'])

            num_luminarias         = int(request.POST['num_luminarias'])
            lamp_luminarias        = int(request.POST['lamp_luminarias'])
            potencia_lamp          = Decimal(request.POST['potencia_lamp'])
            horas_mes              = int(request.POST['consumo_mensual_horas'])

            potencia_total = num_luminarias * lamp_luminarias * potencia_lamp / 1000
            consumo_mensual = potencia_total * horas_mes

            inv = InventarioLuminarias(
                unidad_responsable    = user.unidad_responsable,
                periodo               = periodo_activo,               # aquí
                edificio              = edificio,
                nivel                 = request.POST['nivel'],
                area                  = area,
                tipo_lampara          = request.POST['tipo_lampara'].upper(),
                num_luminarias        = num_luminarias,
                lamp_luminarias       = lamp_luminarias,
                potencia_lamp         = potencia_lamp,
                potencia_total_lum    = potencia_total,
                consumo_mensual_horas = horas_mes,
                consumo_mensual       = consumo_mensual,
                creado_por            = user
            )
            inv.save()
            messages.success(request, "Registro guardado exitosamente.")
            return redirect('listar_inventario_luminarias')

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'Capturistas/Inventarios/Luminarias/add_form.html', {
        'edificios'            : edificios,
        'niveles'              : niveles,
        'areas_filtradas'      : areas_filtradas,
        'edificio_seleccionado': edificio_id,
        'nivel_seleccionado'   : nivel_sel
    })

@never_cache
@login_required_custom
def listar_inventario_luminarias(request):
    """ 
    Listar todos los registros de inventario de luminarias.

    - Verifica que el usuario esté logueado y tenga una sesión activa.  
    - Obtiene el usuario logueado y su unidad responsable.
    - Obtiene los registros de inventario de luminarias para la unidad responsable.
    - Verifica si hay un periodo activo de inventario.
    - Renderiza la plantilla con los registros y el periodo activo.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')
    
    now = datetime.now()

    periodo_activo = PeriodoInventario.objects(
        fecha_inicio__lte=now,
        fecha_fin__gte=now,
        status="Activo",
        activo=True
    ).first()

    if not periodo_activo:
        return render(request, 'Capturistas/Inventarios/Luminarias/inventario_lista.html', {
            'registros': [],
            'periodo_activo': None
        })

    registros = InventarioLuminarias.objects(
        unidad_responsable=user.unidad_responsable,
        creado_por=user,
        periodo=periodo_activo 
    ).order_by('-fecha_registro')

    return render(request, 'Capturistas/Inventarios/Luminarias/inventario_lista.html', {
        'registros': registros,
        'periodo_activo': periodo_activo
    })

@never_cache
@login_required_custom
def editar_inventario_luminarias(request, id):
    """
    Editar un registro de inventario de luminarias.
    - Verifica que el usuario esté logueado y tenga una sesión activa.
    - Obtiene el usuario logueado y su unidad responsable.
    - Obtiene el registro de inventario a editar.
    - Filtra los edificios y áreas según el registro.
    - Procesa el formulario de edición.
    - Actualiza los datos del inventario y redirige a la lista de inventarios.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    try:
        inventario = InventarioLuminarias.objects.get(id=id, unidad_responsable=user.unidad_responsable)
    except InventarioLuminarias.DoesNotExist:
        messages.error(request, "Registro no encontrado.")
        return redirect('listar_inventario_luminarias')

    edificios = Edificio.objects(unidad_responsable=user.unidad_responsable)
    niveles = NIVELES
    areas_filtradas = Area.objects(edificio=inventario.edificio)

    if request.method == 'POST':
        try:
            edificio = Edificio.objects.get(id=request.POST.get('edificio'))
            area = Area.objects.get(id=request.POST.get('area'))
            nivel = request.POST.get('nivel')

            inventario.edificio = edificio
            inventario.area = area
            inventario.nivel = nivel
            inventario.tipo_lampara = request.POST.get('tipo_lampara')
            inventario.num_luminarias = int(request.POST.get('num_luminarias'))
            inventario.lamp_luminarias = int(request.POST.get('lamp_luminarias'))
            inventario.potencia_lamp = Decimal(request.POST.get('potencia_lamp'))
            inventario.potencia_total_lum = inventario.num_luminarias * inventario.lamp_luminarias * inventario.potencia_lamp / 1000
            inventario.consumo_mensual_horas = int(request.POST.get('consumo_mensual_horas'))
            inventario.consumo_mensual = inventario.potencia_total_lum * inventario.consumo_mensual_horas
            inventario.actualizado_por = user
            inventario.ultima_actualizacion = datetime.now()
            inventario.save()
            messages.success(request, "Registro actualizado correctamente.")
            return redirect('listar_inventario_luminarias')
        except Exception as e:
            messages.error(request, f"Error al actualizar: {e}")

    return render(request, 'Capturistas/Inventarios/Luminarias/edit_form.html', {
        'inventario': inventario,
        'edificios': edificios,
        'niveles': niveles,
        'areas_filtradas': areas_filtradas
    })

@never_cache
@login_required_custom
def eliminar_inventario_luminarias(request, id):
    """
    Eliminar un registro de inventario de luminarias.

    - Verifica que el usuario esté logueado y tenga una sesión activa.  
    - Obtiene el usuario logueado y su unidad responsable.
    - Obtiene el registro de inventario a eliminar.
    - Elimina el registro y redirige a la lista de inventarios con un mensaje de éxito.
    """

    user = get_user(request)
    if not user:
        return redirect('login')

    try:
        registro = InventarioLuminarias.objects.get(id=id, unidad_responsable=user.unidad_responsable)
        registro.delete()
        messages.success(request, "Registro eliminado correctamente.")
    except InventarioLuminarias.DoesNotExist:
        messages.error(request, "No se encontró el registro.")

    return redirect('listar_inventario_luminarias')

@never_cache
@login_required_custom
def obtener_areas_luminarias(request):
    """
    Obtener áreas filtradas por edificio para el inventario de luminarias.  

    - Verifica que el usuario esté logueado y tenga una sesión activa.
    - Obtiene el ID del edificio desde la solicitud.
    - Retorna un JSON con las áreas del edificio seleccionado.
    """

    edificio_id = request.GET.get('edificio_id')
    if not edificio_id:
        return JsonResponse([], safe=False)

    try:
        areas = Area.objects(edificio=edificio_id)
        data = [{'id': str(area.id), 'nombre': area.nombre} for area in areas]
        return JsonResponse(data, safe=False)
    except Exception:
        return JsonResponse([], safe=False)
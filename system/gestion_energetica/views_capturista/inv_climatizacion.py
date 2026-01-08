from datetime import datetime

from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect

from system.models import NIVELES, Area, Edificio, InventarioClimatizacion, PeriodoInventario
from system.decorators import login_required_custom
from system.views import get_user


# Vistas de funciones de inventario energetico de aires acondicionados
@never_cache
@login_required_custom
def registrar_inventario_climatizacion(request):
    """
    Registrar un nuevo inventario de climatización.

    Esta vista permite a los capturistas registrar un nuevo inventario de equipos de climatización,
    incluyendo detalles como edificio, área, tipo de clima, marca, modelo, capacidad, voltaje, amperaje,
    potencia, potencia total y horas de uso mensual.
    Se asegura de que el usuario tenga el rol de capturista y que haya un periodo de inventario activo.
    Si no hay un periodo activo, se muestra un mensaje de error.
    """

    user = get_user(request)
    if not user or user.rol != "capturista":
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    edificios = Edificio.objects(unidad_responsable=user.unidad_responsable)
    areas = Area.objects(unidad_responsable=user.unidad_responsable)

    # Obtener periodo activo
    periodo_activo = PeriodoInventario.objects(status="Activo").first()
    if not periodo_activo:
        messages.error(request, "No hay un periodo de inventario activo.")
        return redirect('listar_inventario_climatizacion')

    if request.method == 'POST':
        try:
            edificio = Edificio.objects.get(id=request.POST.get('edificio'))
            area = Area.objects.get(id=request.POST.get('area'))
            nivel = request.POST.get('nivel')
            tipo_clima = request.POST.get('tipo_clima').strip().upper()

            marca = request.POST.get('marca')
            modelo = request.POST.get('modelo')
            capacidad = int(request.POST.get('capacidad'))
            voltaje = int(request.POST.get('voltaje'))
            amperaje = Decimal(request.POST.get('amperaje'))
            potencia = Decimal(request.POST.get('potencia'))
            potencia_total = Decimal(request.POST.get('potencia_total'))
            horas_mes = Decimal(request.POST.get('horas_mes'))

            consumo_mensual = (potencia_total * horas_mes).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            InventarioClimatizacion(
                unidad_responsable=user.unidad_responsable,
                edificio=edificio,
                nivel=nivel,
                area=area,
                tipo_clima=tipo_clima,
                marca=marca,
                modelo=modelo,
                capacidad=capacidad,
                voltaje=voltaje,
                amperaje=amperaje,
                potencia=potencia,
                potencia_total=potencia_total,
                horas_mes=horas_mes,
                consumo_mensual=consumo_mensual,
                creado_por=user,
                periodo=periodo_activo  # Se guarda aquí
            ).save()

            messages.success(request, "Registro de inventario guardado correctamente.")
            return redirect('listar_inventario_climatizacion')

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'Capturistas/Inventarios/Climatizacion/add_form.html', {
        'edificios': edificios,
        'areas': areas,
        'niveles': NIVELES
    })

@never_cache
@login_required_custom
def listar_inventario_climatizacion(request):
    """
    Listar los registros de inventario de climatización.

    Esta vista permite a los capturistas ver los registros de inventario de equipos de climatización
    que han sido creados por ellos. Se asegura de que el usuario tenga el rol de capturista y que haya
    un periodo de inventario activo.
    Si no hay un periodo activo, se muestra un mensaje de error.
    """

    user = get_user(request)
    if not user or user.rol != "capturista":
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    now = datetime.now()

    periodo_activo = PeriodoInventario.objects(
        fecha_inicio__lte=now,
        fecha_fin__gte=now,
        status="Activo",
        activo=True
    ).first()

    if not periodo_activo:
        return render(request, 'Capturistas/Inventarios/Climatizacion/inventario_lista.html', {
            'registros': [],
            'periodo_activo': None
        })

    registros = InventarioClimatizacion.objects(
        unidad_responsable=user.unidad_responsable,
        creado_por=user,
        periodo=periodo_activo 
    ).order_by('-fecha_registro')

    return render(request, 'Capturistas/Inventarios/Climatizacion/inventario_lista.html', {
        'registros': registros,
        'periodo_activo': periodo_activo
    })

@never_cache
@login_required_custom
def editar_inventario_climatizacion(request, id):
    """
    Editar un registro de inventario de climatización.

    Esta vista permite a los capturistas editar un registro existente de inventario de equipos de climatización.
    Se asegura de que el usuario tenga el rol de capturista y que el registro pertenezca al usuario actual.
    Si no hay un periodo activo, se muestra un mensaje de error.
    """

    user = get_user(request)
    if not user:
        return redirect('login')

    inventario = InventarioClimatizacion.objects.get(id=id)

    edificios = Edificio.objects(unidad_responsable=user.unidad_responsable)
    niveles = NIVELES
    areas_filtradas = Area.objects(edificio=inventario.edificio)

    if request.method == 'POST':
        inventario.edificio = Edificio.objects.get(id=request.POST.get('edificio'))
        inventario.nivel = request.POST.get('nivel')
        inventario.area = Area.objects.get(id=request.POST.get('area'))
        inventario.tipo_clima = request.POST.get('tipo_clima')
        inventario.marca = request.POST.get('marca')
        inventario.modelo = request.POST.get('modelo')
        inventario.capacidad = int(request.POST.get('capacidad'))
        inventario.voltaje = int(request.POST.get('voltaje'))
        inventario.amperaje = Decimal(request.POST.get('amperaje'))
        inventario.potencia = Decimal(request.POST.get('potencia'))
        inventario.potencia_total = Decimal(request.POST.get('potencia_total'))
        inventario.horas_mes = Decimal(request.POST.get('horas_mes'))
        inventario.consumo_mensual = inventario.potencia_total * inventario.horas_mes
        inventario.actualizado_por = user
        inventario.ultima_actualizacion = datetime.now()
        inventario.save()

        messages.success(request, "Registro actualizado correctamente.")
        return redirect('listar_inventario_climatizacion')

    return render(request, 'Capturistas/Inventarios/Climatizacion/edit_form.html', {
        'inventario': inventario,
        'edificios': edificios,
        'niveles': niveles,
        'areas_filtradas': areas_filtradas
    })

@never_cache
@login_required_custom
def eliminar_inventario_climatizacion(request, id):
    """
    Eliminar un registro de inventario de climatización.

    Esta vista permite a los capturistas eliminar un registro de inventario de equipos de climatización.
    Se asegura de que el usuario tenga el rol de capturista y que el registro pertenezca al usuario actual.
    Si no hay un periodo activo, se muestra un mensaje de error.
    """

    user = get_user(request)
    if not user:
        messages.error(request, "Sesión expirada.")
        return redirect('login')

    try:
        registro = InventarioClimatizacion.objects.get(id=id)
        if registro.creado_por != user:
            messages.error(request, "No tienes permiso para eliminar este registro.")
            return redirect('listar_inventario_climatizacion')
        registro.delete()
        messages.success(request, "Registro eliminado correctamente.")
    except InventarioClimatizacion.DoesNotExist:
        messages.error(request, "Registro no encontrado.")

    return redirect('listar_inventario_climatizacion')

@never_cache
@login_required_custom
def obtener_areas_por_edificio(request):
    """ 
    Obtener áreas por edificio.

    Esta vista recibe un ID de edificio y devuelve una lista de áreas asociadas a ese edificio en formato JSON.
    Si no se proporciona un ID de edificio, se devuelve una lista vacía.
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
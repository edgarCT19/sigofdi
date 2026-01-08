from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages
from django.shortcuts import render, redirect

from mongoengine.errors import DoesNotExist

from system.models import NIVELES,InventarioClimatizacion, Edificio, Area, PeriodoInventario, UnidadResponsable
from system.views import get_user
from system.decorators import login_required_custom
from system.gestion_energetica.views_admin.utils import is_admin, get_periodo_activo, parse_decimal


@never_cache
@login_required_custom
def listado_inventario_climatizacion(request):
    """
    Vista para listar inventarios de climatización.
    - Restringida a usuarios autenticados con el decorador login_required_custom.
    - never_cache: evita el almacenamiento en caché de esta vista.
    - Si el usuario no es admin, redirige al login con un mensaje de error.
    - Excluye a los false activos (dado de baja).
    """

    climatizacion = InventarioClimatizacion.objects(activo__ne=False).order_by('fecha_registro')

    return render(request, "systemsigo/Inventarios/Climatizacion/lista_climatizacion.html", {
        "climatizacion": climatizacion
    })

@never_cache
@login_required_custom
def registrar_inventario_climatizacion_admin(request):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    # --- Datos base para el formulario ---
    urs = UnidadResponsable.objects.order_by('nombre')
    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')

    # Pre-selección opcional
    ur_sel_id = request.POST.get('unidad_responsable') or request.GET.get('ur')
    periodo_sel_id = request.POST.get('periodo') or request.GET.get('periodo')

    ur_sel = UnidadResponsable.objects(id=ur_sel_id).first() if ur_sel_id else None
    edificios = Edificio.objects(unidad_responsable=ur_sel) if ur_sel else []
    areas = Area.objects(unidad_responsable=ur_sel) if ur_sel else []

    if request.method == 'POST':
        try:
            ur = UnidadResponsable.objects.get(id=request.POST.get('unidad_responsable'))
            periodo = PeriodoInventario.objects.get(id=request.POST.get('periodo'))
            edificio = Edificio.objects.get(id=request.POST.get('edificio'))
            area = Area.objects.get(id=request.POST.get('area'))

            nivel = request.POST.get('nivel')
            tipo_clima = request.POST.get('tipo_clima', '').strip().upper()
            marca = request.POST.get('marca')
            modelo = request.POST.get('modelo')
            capacidad = int(request.POST.get('capacidad') or 0)
            voltaje = int(request.POST.get('voltaje') or 0)
            amperaje = Decimal(request.POST.get('amperaje') or 0)
            potencia = Decimal(request.POST.get('potencia') or 0)
            potencia_total = Decimal(request.POST.get('potencia_total') or 0)
            horas_mes = Decimal(request.POST.get('horas_mes') or 0)

            consumo_mensual = (potencia_total * horas_mes).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            InventarioClimatizacion(
                unidad_responsable=ur,
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
                periodo=periodo
            ).save()

            messages.success(request, "Registro de climatización creado correctamente.")
            return redirect('listado_inventario_climatizacion')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe (UR/Periodo/Edificio/Área).")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'systemsigo/Inventarios/Climatizacion/add_form.html', {
        'urs': urs,
        'periodos': periodos,
        'edificios': edificios,
        'areas': areas,
        'niveles': NIVELES,
    })


@never_cache
@login_required_custom
def editar_inventario_climatizacion_admin(request, climatizacion_id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    # --- Obtener el registro ---
    climatizacion = InventarioClimatizacion.objects(id=climatizacion_id).first()
    if not climatizacion:
        messages.error(request, "Registro no encontrado.")
        return redirect('listado_inventario_climatizacion')

    # --- Datos para formulario ---
    urs = UnidadResponsable.objects.order_by('nombre')
    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')
    ur_sel = climatizacion.unidad_responsable
    edificios = Edificio.objects(unidad_responsable=ur_sel)
    areas = Area.objects(unidad_responsable=ur_sel)

    if request.method == 'POST':
        try:
            ur = UnidadResponsable.objects.get(id=request.POST.get('unidad_responsable'))
            periodo = PeriodoInventario.objects.get(id=request.POST.get('periodo'))
            edificio = Edificio.objects.get(id=request.POST.get('edificio'))
            area = Area.objects.get(id=request.POST.get('area'))

            climatizacion.unidad_responsable = ur
            climatizacion.edificio = edificio
            climatizacion.nivel = request.POST.get('nivel')
            climatizacion.area = area
            climatizacion.tipo_clima = request.POST.get('tipo_clima', '').strip().upper()
            climatizacion.marca = request.POST.get('marca')
            climatizacion.modelo = request.POST.get('modelo')
            climatizacion.capacidad = int(request.POST.get('capacidad') or 0)
            climatizacion.voltaje = Decimal(request.POST.get('voltaje') or 0)
            climatizacion.amperaje = Decimal(request.POST.get('amperaje') or 0)
            climatizacion.potencia = Decimal(request.POST.get('potencia') or 0)
            climatizacion.potencia_total = Decimal(request.POST.get('potencia_total') or 0)
            climatizacion.horas_mes = Decimal(request.POST.get('horas_mes') or 0)
            climatizacion.consumo_mensual = (climatizacion.potencia_total * climatizacion.horas_mes).quantize(Decimal('0.01'))
            climatizacion.actualizado_por = user
            climatizacion.ultima_actualizacion = datetime.now()
            climatizacion.periodo = periodo

            climatizacion.save()
            messages.success(request, "Inventario actualizado correctamente.")
            return redirect('listado_inventario_climatizacion')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe (UR/Periodo/Edificio/Área).")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'systemsigo/Inventarios/Climatizacion/edit_form.html', {
        'climatizacion': climatizacion,
        'urs': urs,
        'periodos': periodos,
        'edificios': edificios,
        'areas': areas,
        'niveles': NIVELES,
    })


@never_cache
@login_required_custom
def eliminar_inventario_climatizacion_admin(request, climatizacion_id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        return JsonResponse({"success": False, "error": "Acceso denegado"})

    climatizacion = InventarioClimatizacion.objects(id=climatizacion_id).first()
    if not climatizacion:
        return JsonResponse({"success": False, "error": "Registro no encontrado"})

    try:
        climatizacion.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

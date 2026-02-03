from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.shortcuts import render, redirect

from mongoengine.errors import DoesNotExist

from system.models import (
    NIVELES,
    InventarioClimatizacion,
    Edificio,
    Area,
    PeriodoInventario,
    UnidadResponsable
)
from system.views import get_user
from system.decorators import login_required_custom


@never_cache
@login_required_custom
def registrar_inventario_climatizacion_responsable_energia(request):
    user = get_user(request)
    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect('encargado_ur')

    ur_ids = [ur.id for ur in user.unidad_responsable]
    urs = UnidadResponsable.objects(id__in=ur_ids).order_by('nombre')

    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')

    ur_sel_id = request.POST.get('unidad_responsable') or request.GET.get('ur')

    ur_sel = None
    if ur_sel_id and urs.filter(id=ur_sel_id).first():
        ur_sel = UnidadResponsable.objects(id=ur_sel_id).first()

    edificios = Edificio.objects(unidad_responsable=ur_sel) if ur_sel else []
    areas = Area.objects(unidad_responsable=ur_sel) if ur_sel else []

    if request.method == 'POST':
        try:
            ur_id = request.POST.get('unidad_responsable')

            if urs.filter(id=ur_id).first() is None:
                messages.error(
                    request,
                    "No tienes permiso para esta Unidad Responsable."
                )
                return redirect(request.path)

            ur = UnidadResponsable.objects.get(id=ur_id)
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
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
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

            messages.success(
                request,
                "Inventario de climatización registrado correctamente."
            )
            return redirect('listar_climatizacion_encargado')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(
        request,
        'Encargado_UR/Inventarios/Climatizacion/add_form.html',
        {
            'urs': urs,
            'periodos': periodos,
            'edificios': edificios,
            'areas': areas,
            'niveles': NIVELES,
        }
    )

@never_cache
@login_required_custom
def editar_inventario_climatizacion_responsable_energia(request, climatizacion_id):
    user = get_user(request)
    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect('encargado_ur')

    ur_ids = [ur.id for ur in user.unidad_responsable]
    urs = UnidadResponsable.objects(id__in=ur_ids).order_by('nombre')

    climatizacion = InventarioClimatizacion.objects(id=climatizacion_id).first()
    if not climatizacion:
        messages.error(request, "Registro no encontrado.")
        return redirect('listar_climatizacion_encargado')

    if climatizacion.unidad_responsable.id not in ur_ids:
        messages.error(request, "No tienes permiso para editar este registro.")
        return redirect('listar_climatizacion_encargado')

    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')

    ur_sel = climatizacion.unidad_responsable
    edificios = Edificio.objects(unidad_responsable=ur_sel)
    areas = Area.objects(unidad_responsable=ur_sel)

    if request.method == 'POST':
        try:
            ur_id = request.POST.get('unidad_responsable')

            if urs.filter(id=ur_id).first() is None:
                messages.error(request, "No tienes permiso para esta Unidad Responsable.")
                return redirect(request.path)

            ur = UnidadResponsable.objects.get(id=ur_id)
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

            climatizacion.consumo_mensual = (
                climatizacion.potencia_total * climatizacion.horas_mes
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            climatizacion.actualizado_por = user
            climatizacion.ultima_actualizacion = datetime.now()
            climatizacion.periodo = periodo

            climatizacion.save()

            messages.success(request, "Inventario actualizado correctamente.")
            return redirect('listar_climatizacion_encargado')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(
        request,
        'Encargado_UR/Inventarios/Climatizacion/edit_form.html',
        {
            'climatizacion': climatizacion,
            'urs': urs,
            'periodos': periodos,
            'edificios': edificios,
            'areas': areas,
            'niveles': NIVELES,
        }
    )
    
@never_cache
@login_required_custom
def dar_baja_inventario_climatizacion_responsable_energia(request, his_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("encargado_ur")

    try:
        his = InventarioClimatizacion.objects.get(id=his_id)
    except DoesNotExist:
        messages.error(request, "Inventario no encontrado.")
        return redirect('listar_climatizacion_encargado')

    if his.unidad_responsable not in user.unidad_responsable:
        messages.error(
            request,
            "No tienes permiso para dar de baja este registro."
        )
        return redirect('listar_climatizacion_encargado')

    his.activo = False
    his.fecha_baja = datetime.now()
    his.dado_baja_por = user
    his.save()

    messages.success(
        request,
        "Registro de climatización dado de baja correctamente."
    )

    return redirect('listar_climatizacion_encargado')

@never_cache
@login_required_custom
def historial_climatizacion_encargado(request):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("encargado_ur")

    ur_ids = [ur.id for ur in user.unidad_responsable]

    registros_baja = InventarioClimatizacion.objects(
        activo=False,
        unidad_responsable__in=ur_ids
    ).order_by('-fecha_baja')

    return render(
        request,
        'Encargado_UR/Inventarios/Climatizacion/bajas.html',
        {
            'registros': registros_baja
        }
    )

@never_cache
@login_required_custom
def restaurar_registro_climatizacion_encargado(request, registro_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("encargado_ur")

    try:
        registro = InventarioClimatizacion.objects.get(id=registro_id)
    except DoesNotExist:
        messages.error(request, "Registro no encontrado.")
        return redirect('historial_climatizacion_encargado')

    if registro.unidad_responsable not in user.unidad_responsable:
        messages.error(
            request,
            "No tienes permiso para restaurar este registro."
        )
        return redirect('historial_climatizacion_encargado')

    registro.activo = True
    registro.fecha_reactivacion = datetime.now()
    registro.reactivado_por = user
    registro.save()

    messages.success(
        request,
        "Registro de climatización restaurado correctamente."
    )

    return redirect('historial_climatizacion_encargado')

@never_cache
@login_required_custom
def eliminar_inventario_climatizacion_encargado(request, climatizacion_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        return JsonResponse({
            "success": False,
            "error": "Acceso denegado"
        })

    climatizacion = InventarioClimatizacion.objects(
        id=climatizacion_id
    ).first()

    if not climatizacion:
        return JsonResponse({
            "success": False,
            "error": "Registro no encontrado"
        })

    if climatizacion.unidad_responsable not in user.unidad_responsable:
        return JsonResponse({
            "success": False,
            "error": "No tienes permiso para eliminar este registro"
        })

    try:
        climatizacion.delete()
        messages.success(request, "Registro eliminado correctamente.")
        return JsonResponse({"success": True, "message": "Registro eliminado correctamente."})
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })
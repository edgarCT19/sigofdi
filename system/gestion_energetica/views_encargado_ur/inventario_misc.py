from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.shortcuts import render, redirect

from mongoengine.errors import DoesNotExist

from system.models import (
    NIVELES,
    InventarioMiscelaneos,
    Edificio,
    Area,
    PeriodoInventario,
    UnidadResponsable
)
from system.views import get_user
from system.decorators import login_required_custom

@never_cache
@login_required_custom
def registrar_inventario_miscelaneos_responsable_energia(request):
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
            marca = request.POST.get('marca', '').strip().upper()
            miscelaneos = request.POST.get('miscelaneos', '').strip().upper()
            modelo = request.POST.get('modelo', '').strip().upper()
            voltaje = Decimal(request.POST.get('voltaje') or 0)
            amperaje = Decimal(request.POST.get('amperaje') or 0)
            potencia = Decimal(request.POST.get('potencia') or 0)
            potencia_total = Decimal(request.POST.get('potencia_total') or 0)
            horas_mes = Decimal(request.POST.get('horas_mes') or 0)

            consumo_mensual = (
                potencia_total * horas_mes
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            InventarioMiscelaneos(
                unidad_responsable=ur,
                edificio=edificio,
                nivel=nivel,
                area=area,
                marca=marca,
                miscelaneos=miscelaneos,
                modelo=modelo,
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
                "Inventario de misceláneos registrado correctamente."
            )
            return redirect('listar_miscelaneos_encargado')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(
        request,
        'Encargado_UR/Inventarios/Miscelaneos/add_form.html',
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
def editar_inventario_miscelaneos_responsable_energia(request, miscelaneos_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect('encargado_ur')

    ur_ids = [ur.id for ur in user.unidad_responsable]
    urs = UnidadResponsable.objects(id__in=ur_ids).order_by('nombre')

    miscelaneos = InventarioMiscelaneos.objects(id=miscelaneos_id).first()
    if not miscelaneos:
        messages.error(request, "Registro no encontrado.")
        return redirect('listar_miscelaneos_encargado')

    if miscelaneos.unidad_responsable.id not in ur_ids:
        messages.error(request, "No tienes permiso para editar este registro.")
        return redirect('listar_miscelaneos_encargado')

    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')
    ur_sel = miscelaneos.unidad_responsable
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

            miscelaneos.unidad_responsable = ur
            miscelaneos.edificio = edificio
            miscelaneos.nivel = request.POST.get('nivel')
            miscelaneos.area = area
            miscelaneos.marca = request.POST.get('marca', '').strip().upper()
            miscelaneos.miscelaneos = request.POST.get('miscelaneos', '').strip().upper()
            miscelaneos.modelo = request.POST.get('modelo', '').strip().upper()
            miscelaneos.voltaje = Decimal(request.POST.get('voltaje') or 0)
            miscelaneos.amperaje = Decimal(request.POST.get('amperaje') or 0)
            miscelaneos.potencia = Decimal(request.POST.get('potencia') or 0)
            miscelaneos.potencia_total = Decimal(request.POST.get('potencia_total') or 0)
            miscelaneos.horas_mes = Decimal(request.POST.get('horas_mes') or 0)

            miscelaneos.consumo_mensual = (
                miscelaneos.potencia_total * miscelaneos.horas_mes
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            miscelaneos.actualizado_por = user
            miscelaneos.ultima_actualizacion = datetime.now()
            miscelaneos.periodo = periodo

            miscelaneos.save()

            messages.success(request, "Inventario de misceláneos actualizado correctamente.")
            return redirect('listar_miscelaneos_encargado')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(
        request,
        'Encargado_UR/Inventarios/Miscelaneos/edit_form.html',
        {
            'miscelaneos': miscelaneos,
            'urs': urs,
            'periodos': periodos,
            'edificios': edificios,
            'areas': areas,
            'niveles': NIVELES,
        }
    )
 
@never_cache
@login_required_custom
def dar_baja_inventario_miscelaneos_responsable_energia(request, his_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("encargado_ur")

    try:
        his = InventarioMiscelaneos.objects.get(id=his_id)
    except DoesNotExist:
        messages.error(request, "Inventario no encontrado.")
        return redirect('listar_miscelaneos_encargado')

    if his.unidad_responsable not in user.unidad_responsable:
        messages.error(
            request,
            "No tienes permiso para dar de baja este registro."
        )
        return redirect('listar_miscelaneos_encargado')

    his.activo = False
    his.fecha_baja = datetime.now()
    his.dado_baja_por = user
    his.save()

    messages.success(
        request,
        "Registro de misceláneos dado de baja correctamente."
    )

    return redirect('listar_miscelaneos_encargado')

@never_cache
@login_required_custom
def historial_miscelaneos_encargado(request):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("encargado_ur")

    ur_ids = [ur.id for ur in user.unidad_responsable]

    registros_baja = InventarioMiscelaneos.objects(
        activo=False,
        unidad_responsable__in=ur_ids
    ).order_by('-fecha_baja')

    return render(
        request,
        'Encargado_UR/Inventarios/Miscelaneos/bajas.html',
        {
            'registros': registros_baja
        }
    )

@never_cache
@login_required_custom
def restaurar_registro_miscelaneos_encargado(request, registro_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("encargado_ur")

    try:
        registro = InventarioMiscelaneos.objects.get(id=registro_id)
    except DoesNotExist:
        messages.error(request, "Registro no encontrado.")
        return redirect('historial_miscelaneos_encargado')

    if registro.unidad_responsable not in user.unidad_responsable:
        messages.error(
            request,
            "No tienes permiso para restaurar este registro."
        )
        return redirect('historial_miscelaneos_encargado')

    registro.activo = True
    registro.fecha_reactivacion = datetime.now()
    registro.reactivado_por = user
    registro.save()

    messages.success(
        request,
        "Registro de misceláneos restaurado correctamente."
    )

    return redirect('historial_miscelaneos_encargado')

@never_cache
@login_required_custom
def eliminar_inventario_miscelaneos_encargado(request, miscelaneo_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        return JsonResponse({
            "success": False,
            "error": "Acceso denegado"
        })

    miscelaneo = InventarioMiscelaneos.objects(
        id=miscelaneo_id
    ).first()

    if not miscelaneo:
        return JsonResponse({
            "success": False,
            "error": "Registro no encontrado"
        })

    if miscelaneo.unidad_responsable not in user.unidad_responsable:
        return JsonResponse({
            "success": False,
            "error": "No tienes permiso para eliminar este registro"
        })

    try:
        miscelaneo.delete()
        messages.success(request, "Registro eliminado correctamente.")
        return JsonResponse({"success": True, "message": "Registro eliminado correctamente."})
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })
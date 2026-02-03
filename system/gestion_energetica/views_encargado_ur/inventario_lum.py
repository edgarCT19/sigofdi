from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.shortcuts import render, redirect

from mongoengine.errors import DoesNotExist

from system.models import (
    NIVELES,
    InventarioLuminarias,
    Edificio,
    Area,
    PeriodoInventario,
    UnidadResponsable
)
from system.views import get_user
from system.decorators import login_required_custom

@never_cache
@login_required_custom
def registrar_inventario_luminarias_responsable_energia(request):
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
                messages.error(request, "No tienes permiso para esta Unidad Responsable.")
                return redirect(request.path)

            ur = UnidadResponsable.objects.get(id=ur_id)
            periodo = PeriodoInventario.objects.get(id=request.POST.get('periodo'))
            edificio = Edificio.objects.get(id=request.POST.get('edificio'))
            area = Area.objects.get(id=request.POST.get('area'))
            nivel = request.POST.get('nivel')

            tipo_lampara = request.POST.get('tipo_lampara', '').strip().upper()
            num_luminarias = int(request.POST.get('num_luminarias') or 0)
            lamp_luminarias = int(request.POST.get('lamp_luminarias') or 0)
            potencia_lamp = Decimal(request.POST.get('potencia_lamp') or 0)
            consumo_mensual_horas = int(request.POST.get('consumo_mensual_horas') or 0)

            potencia_total = (
                num_luminarias * lamp_luminarias * potencia_lamp / 1000
            ).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

            consumo_mensual = (
                potencia_total * consumo_mensual_horas
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            InventarioLuminarias(
                unidad_responsable=ur,
                edificio=edificio,
                nivel=nivel,
                area=area,
                tipo_lampara=tipo_lampara,
                num_luminarias=num_luminarias,
                lamp_luminarias=lamp_luminarias,
                potencia_lamp=potencia_lamp,
                potencia_total_lum=potencia_total,
                consumo_mensual_horas=consumo_mensual_horas,
                consumo_mensual=consumo_mensual,
                creado_por=user,
                periodo=periodo
            ).save()

            messages.success(
                request,
                "Inventario de luminarias registrado correctamente."
            )
            return redirect('listar_luminarias_encargado')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(
        request,
        'Encargado_UR/Inventarios/Luminarias/add_form.html',
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
def editar_inventario_luminarias_responsable_energia(request, luminarias_id):
    user = get_user(request)
    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect('encargado_ur')

    # --- URs permitidas ---
    ur_ids = [ur.id for ur in user.unidad_responsable]
    urs = UnidadResponsable.objects(id__in=ur_ids).order_by('nombre')

    # --- Obtener registro ---
    luminarias = InventarioLuminarias.objects(id=luminarias_id).first()
    if not luminarias:
        messages.error(request, "Registro no encontrado.")
        return redirect('listar_luminarias_encargado')

    # --- Seguridad: validar pertenencia ---
    if luminarias.unidad_responsable.id not in ur_ids:
        messages.error(request, "No tienes permiso para editar este registro.")
        return redirect('listar_luminarias_encargado')

    # --- Datos base ---
    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')
    ur_sel = luminarias.unidad_responsable
    edificios = Edificio.objects(unidad_responsable=ur_sel)
    areas = Area.objects(unidad_responsable=ur_sel)

    if request.method == 'POST':
        try:
            ur_id = request.POST.get('unidad_responsable')

            # Validar UR seleccionada
            if urs.filter(id=ur_id).first() is None:
                messages.error(request, "No tienes permiso para esta Unidad Responsable.")
                return redirect(request.path)

            ur = UnidadResponsable.objects.get(id=ur_id)
            periodo = PeriodoInventario.objects.get(id=request.POST.get('periodo'))
            edificio = Edificio.objects.get(id=request.POST.get('edificio'))
            area = Area.objects.get(id=request.POST.get('area'))

            # --- Asignaciones ---
            luminarias.unidad_responsable = ur
            luminarias.edificio = edificio
            luminarias.nivel = request.POST.get('nivel')
            luminarias.area = area
            luminarias.tipo_lampara = request.POST.get(
                'tipo_lampara', ''
            ).strip().upper()

            luminarias.num_luminarias = int(
                request.POST.get('num_luminarias') or 0
            )
            luminarias.lamp_luminarias = int(
                request.POST.get('lamp_luminarias') or 0
            )
            luminarias.potencia_lamp = Decimal(
                request.POST.get('potencia_lamp') or 0
            )
            luminarias.consumo_mensual_horas = int(
                request.POST.get('consumo_mensual_horas') or 0
            )

            luminarias.potencia_total_lum = (
                luminarias.num_luminarias *
                luminarias.lamp_luminarias *
                luminarias.potencia_lamp / 1000
            ).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

            luminarias.consumo_mensual = (
                luminarias.potencia_total_lum *
                luminarias.consumo_mensual_horas
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            luminarias.actualizado_por = user
            luminarias.ultima_actualizacion = datetime.now()
            luminarias.periodo = periodo

            luminarias.save()

            messages.success(
                request,
                "Inventario de luminarias actualizado correctamente."
            )
            return redirect('listar_luminarias_encargado')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(
        request,
        'Encargado_UR/Inventarios/Luminarias/edit_form.html',
        {
            'luminarias': luminarias,
            'urs': urs,
            'periodos': periodos,
            'edificios': edificios,
            'areas': areas,
            'niveles': NIVELES,
        }
    )

@never_cache
@login_required_custom
def dar_baja_inventario_luminarias_responsable_energia(request, his_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("encargado_ur")

    try:
        his = InventarioLuminarias.objects.get(id=his_id)
    except DoesNotExist:
        messages.error(request, "Inventario no encontrado.")
        return redirect('listar_luminarias_encargado')

    if his.unidad_responsable not in user.unidad_responsable:
        messages.error(
            request,
            "No tienes permiso para dar de baja este registro."
        )
        return redirect('listar_luminarias_encargado')

    try:
        his.activo = False 
        his.actualizado_por = user
        his.ultima_actualizacion = datetime.now()
        his.save()

        messages.success(
            request,
            "El inventario de luminarias fue dado de baja correctamente."
        )

    except Exception as e:
        messages.error(request, f"Ocurrió un error: {e}")

    return redirect('listar_luminarias_encargado')

@never_cache
@login_required_custom
def historial_luminarias_encargado(request):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("encargado_ur")

    ur_ids = [ur.id for ur in user.unidad_responsable]

    registros_baja = InventarioLuminarias.objects(
        activo=False,
        unidad_responsable__in=ur_ids
    ).order_by('-fecha_baja')

    return render(
        request,
        'Encargado_UR/Inventarios/Luminarias/bajas.html',
        {
            'registros': registros_baja
        }
    )

@never_cache
@login_required_custom
def restaurar_registro_luminarias_encargado(request, registro_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        messages.error(request, "Acceso denegado.")
        return redirect("encargado_ur")

    try:
        registro = InventarioLuminarias.objects.get(id=registro_id)
    except DoesNotExist:
        messages.error(request, "Registro no encontrado.")
        return redirect('historial_luminarias_encargado')

    if registro.unidad_responsable not in user.unidad_responsable:
        messages.error(
            request,
            "No tienes permiso para restaurar este registro."
        )
        return redirect('historial_luminarias_encargado')

    registro.activo = True
    registro.fecha_reactivacion = datetime.now()
    registro.reactivado_por = user
    registro.save()

    messages.success(
        request,
        "Registro de luminarias restaurado correctamente."
    )

    return redirect('historial_luminarias_encargado')

@never_cache
@login_required_custom
def eliminar_inventario_luminarias_encargado(request, luminaria_id):
    user = get_user(request)

    if not user or user.rol != "encargado_ur":
        return JsonResponse({
            "success": False,
            "error": "Acceso denegado"
        })

    luminaria = InventarioLuminarias.objects(
        id=luminaria_id
    ).first()

    if not luminaria:
        return JsonResponse({
            "success": False,
            "error": "Registro no encontrado"
        })

    if luminaria.unidad_responsable not in user.unidad_responsable:
        return JsonResponse({
            "success": False,
            "error": "No tienes permiso para eliminar este registro"
        })

    try:
        luminaria.delete()
        messages.success(request, "Registro eliminado correctamente.")
        return JsonResponse({"success": True, "message": "Registro eliminado correctamente."})
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })
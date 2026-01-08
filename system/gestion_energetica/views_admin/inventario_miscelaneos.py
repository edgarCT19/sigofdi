from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages
from django.shortcuts import render, redirect

from system.models import InventarioMiscelaneos, PeriodoInventario, UnidadResponsable, Edificio, Area, NIVELES
from system.views import get_user
from system.decorators import login_required_custom
from system.gestion_energetica.views_admin.utils import is_admin

from decimal import Decimal, ROUND_HALF_UP

from mongoengine.errors import DoesNotExist

from datetime import datetime

@never_cache
@login_required_custom
def listado_inventario_miscelaneos(request):
    """
    Vista para listar inventarios de miscelaneos.
    - Restringida a usuarios autenticados con el decorador login_required_custom.
    - never_cache: evita el almacenamiento en caché de esta vista.
    - Si el usuario no es admin, redirige al login con un mensaje de error.
    """

    miscelaneos = InventarioMiscelaneos.objects(activo__ne=False).order_by('fecha_registro')
    return render(request, "systemsigo/Inventarios/Miscelaneos/lista_miscelaneos.html", {
        "miscelaneos": miscelaneos
    })

@never_cache
@login_required_custom
def registrar_inventario_miscelaneos_admin(request):
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
            marca = request.POST.get('marca', '').strip().upper()
            miscelaneos = request.POST.get('miscelaneos', '').strip().upper()
            modelo = request.POST.get('modelo', '').strip().upper()
            voltaje = Decimal(request.POST.get('voltaje') or 0)
            amperaje = Decimal(request.POST.get('amperaje') or 0)
            potencia = Decimal(request.POST.get('potencia') or 0)
            potencia_total = Decimal(request.POST.get('potencia_total') or 0)
            horas_mes = Decimal(request.POST.get('horas_mes') or 0)

            consumo_mensual = (potencia_total * horas_mes).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

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

            messages.success(request, "Registro de misceláneos creado correctamente.")
            return redirect('listado_inventario_miscelaneos')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe (UR/Periodo/Edificio/Área).")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'systemsigo/Inventarios/Miscelaneos/add_form.html', {
        'urs': urs,
        'periodos': periodos,
        'edificios': edificios,
        'areas': areas,
        'niveles': NIVELES,
    })

@never_cache
@login_required_custom
def editar_inventario_miscelaneos_admin(request, miscelaneos_id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    # --- Obtener el registro ---
    miscelaneos = InventarioMiscelaneos.objects(id=miscelaneos_id).first()
    if not miscelaneos:
        messages.error(request, "Registro no encontrado.")
        return redirect('listado_inventario_miscelaneos')

    # --- Datos para formulario ---
    urs = UnidadResponsable.objects.order_by('nombre')
    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')
    ur_sel = miscelaneos.unidad_responsable
    edificios = Edificio.objects(unidad_responsable=ur_sel)
    areas = Area.objects(unidad_responsable=ur_sel)

    if request.method == 'POST':
        try:
            ur = UnidadResponsable.objects.get(id=request.POST.get('unidad_responsable'))
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
            miscelaneos.consumo_mensual = (miscelaneos.potencia_total * miscelaneos.horas_mes).quantize(Decimal('0.01'))
            miscelaneos.actualizado_por = user
            miscelaneos.ultima_actualizacion = datetime.now()
            miscelaneos.periodo = periodo

            miscelaneos.save()
            messages.success(request, "Inventario de misceláneos actualizado correctamente.")
            return redirect('listado_inventario_miscelaneos')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe (UR/Periodo/Edificio/Área).")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'systemsigo/Inventarios/Miscelaneos/edit_form.html', {
        'miscelaneos': miscelaneos,
        'urs': urs,
        'periodos': periodos,
        'edificios': edificios,
        'areas': areas,
        'niveles': NIVELES,
    })

@never_cache
@login_required_custom
def eliminar_inventario_miscelaneos_admin(request, miscelaneos_id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        return JsonResponse({"success": False, "error": "Acceso denegado"})

    miscelaneos = InventarioMiscelaneos.objects(id=miscelaneos_id).first()
    if not miscelaneos:
        return JsonResponse({"success": False, "error": "Registro no encontrado"})

    try:
        miscelaneos.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

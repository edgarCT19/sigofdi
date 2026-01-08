from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse

from system.models import NIVELES, InventarioLuminarias, PeriodoInventario, UnidadResponsable, Edificio, Area
from system.views import get_user
from system.decorators import login_required_custom
from system.gestion_energetica.views_admin.utils import is_admin

from decimal import Decimal, ROUND_HALF_UP

from mongoengine.errors import DoesNotExist

from datetime import datetime


@never_cache
@login_required_custom
def listado_inventario_luminarias_admin(request):
    """
    Vista para listar inventarios de luminarias.
    - Restringida a usuarios autenticados con el decorador login_required_custom.
    - never_cache: evita el almacenamiento en caché de esta vista.
    - Si el usuario no es admin, redirige al login con un mensaje de error.
    """

    luminarias = InventarioLuminarias.objects.all()
    return render(request, "systemsigo/Inventarios/Luminarias/lista_luminarias.html", {
        "luminarias": luminarias
    })


@never_cache
@login_required_custom
def registrar_inventario_luminarias_admin(request):
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

            tipo_lampara = request.POST.get('tipo_lampara', '').strip().upper()
            num_luminarias = int(request.POST.get('num_luminarias') or 0)
            lamp_luminarias = int(request.POST.get('lamp_luminarias') or 0)
            potencia_lamp = Decimal(request.POST.get('potencia_lamp') or 0)
            potencia_total_lum = Decimal(request.POST.get('potencia_total_lum') or 0)
            consumo_mensual_horas = int(request.POST.get('consumo_mensual_horas') or 0)
            consumo_mensual = Decimal(request.POST.get('consumo_mensual') or 0)

            potencia_total = (num_luminarias * lamp_luminarias * potencia_lamp / 1000).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
            consumo_mensual = (potencia_total * consumo_mensual_horas).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

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

            messages.success(request, "Registro de climatización creado correctamente.")
            return redirect('listado_inventario_luminarias')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe (UR/Periodo/Edificio/Área).")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'systemsigo/Inventarios/Luminarias/add_form.html', {
        'urs': urs,
        'periodos': periodos,
        'edificios': edificios,
        'areas': areas,
        'niveles': NIVELES,
    })

@never_cache
@login_required_custom
def editar_inventario_luminarias_admin(request, luminarias_id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio')

    # --- Obtener el registro ---
    luminarias = InventarioLuminarias.objects(id=luminarias_id).first()
    if not luminarias:
        messages.error(request, "Registro no encontrado.")
        return redirect('listado_inventario_luminarias')

    # --- Datos para formulario ---
    urs = UnidadResponsable.objects.order_by('nombre')
    periodos = PeriodoInventario.objects.order_by('-fecha_inicio')
    ur_sel = luminarias.unidad_responsable
    edificios = Edificio.objects(unidad_responsable=ur_sel)
    areas = Area.objects(unidad_responsable=ur_sel)

    if request.method == 'POST':
        try:
            ur = UnidadResponsable.objects.get(id=request.POST.get('unidad_responsable'))
            periodo = PeriodoInventario.objects.get(id=request.POST.get('periodo'))
            edificio = Edificio.objects.get(id=request.POST.get('edificio'))
            area = Area.objects.get(id=request.POST.get('area'))

            luminarias.unidad_responsable = ur
            luminarias.edificio = edificio
            luminarias.nivel = request.POST.get('nivel')
            luminarias.area = area
            luminarias.tipo_lampara = request.POST.get('tipo_lampara', '').strip().upper()
            luminarias.num_luminarias = int(request.POST.get('num_luminarias') or 0)
            luminarias.lamp_luminarias = int(request.POST.get('lamp_luminarias') or 0)
            luminarias.potencia_lamp = Decimal(request.POST.get('potencia_lamp') or 0)
            luminarias.potencia_total_lum = Decimal(request.POST.get('potencia_total_lum') or 0)
            luminarias.consumo_mensual_horas = int(request.POST.get('consumo_mensual_horas') or 0)
            luminarias.consumo_mensual = (luminarias.potencia_total_lum * luminarias.consumo_mensual_horas).quantize(Decimal('0.01'))
            luminarias.actualizado_por = user
            luminarias.ultima_actualizacion = datetime.now()
            luminarias.periodo = periodo


            luminarias.save()
            messages.success(request, "Inventario actualizado correctamente.")
            return redirect('listado_inventario_luminarias')

        except DoesNotExist:
            messages.error(request, "Alguna referencia no existe (UR/Periodo/Edificio/Área).")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'systemsigo/Inventarios/Luminarias/edit_form.html', {
        'luminarias': luminarias,
        'urs': urs,
        'periodos': periodos,
        'edificios': edificios,
        'areas': areas,
        'niveles': NIVELES,
    })

@never_cache
@login_required_custom
def eliminar_inventario_luminarias_admin(request, luminarias_id):
    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        return JsonResponse({"success": False, "error": "Acceso denegado"})

    luminarias = InventarioLuminarias.objects(id=luminarias_id).first()
    if not luminarias:
        return JsonResponse({"success": False, "error": "Registro no encontrado"})

    try:
        luminarias.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
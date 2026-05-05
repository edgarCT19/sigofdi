from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.db.models import Sum

from datetime import datetime
from collections import defaultdict
import re

import requests

from system.views import get_user
from system.decorators import login_required_custom
from system.models import Area, Edificio, FacturaEnergeticaTriple, FacturaPdbt, InventarioClimatizacion, InventarioLuminarias, InventarioMiscelaneos, PeriodoInventario, Subestacion, UnidadResponsable

# Vistas para el inicio del administrador del sistema
@never_cache
@login_required_custom
def Inicio(request):
    """
    Dashboard principal del sistema.
    Muestra métricas de inventario, consumo energético, facturación e infraestructura.
    """
    def obtener_ur_desde_subestacion(sub):
        try:
            return sub.unidad_responsable.nombre if sub and sub.unidad_responsable else "Sin UR"
        except:
            return "Sin UR"

    # 1. Usuario: nombre del usuario logueado
    usuario = get_user(request)
    primer_nombre = usuario.nombres.split()[0] if usuario.nombres else ""

    # 2. Inventario: cantidad total de equipos por tipo, consumo mensual por tipo de equipo
    total_clima = InventarioClimatizacion.objects.count()
    total_lum = InventarioLuminarias.objects.count()
    total_misc = InventarioMiscelaneos.objects.count()
    total_equipos = total_clima + total_lum + total_misc

    # 3. Consumo energético: consumo mensual por tipo de equipo, consumo total, consumo promedio por equipo
    consumo_clima = sum(float(x.consumo_mensual or 0) for x in InventarioClimatizacion.objects)
    consumo_lum = sum(float(x.consumo_mensual or 0) for x in InventarioLuminarias.objects)
    consumo_misc = sum(float(x.consumo_mensual or 0) for x in InventarioMiscelaneos.objects)

    consumo_total = consumo_clima + consumo_lum + consumo_misc
    consumo_promedio = consumo_total / total_equipos if total_equipos > 0 else 0

    # 4. Facturación: cantidad de facturas pagadas vs no pagadas, porcentaje de pago, total facturación en el periodo, UR con mayor facturación
    pagadas = FacturaEnergeticaTriple.objects(status="Pagada").count()
    no_pagadas = FacturaEnergeticaTriple.objects(status="No pagada").count()

    total_facturas = pagadas + no_pagadas
    porcentaje_pago = (pagadas / total_facturas * 100) if total_facturas > 0 else 0

    # Periodo seleccionado para métricas de facturación
    periodo_input = request.GET.get("periodo")

    if periodo_input:
        try:
            anio, mes = map(int, periodo_input.split("-"))
        except:
            hoy = datetime.now()
            anio, mes = hoy.year, hoy.month
    else:
        hoy = datetime.now()
        anio, mes = hoy.year, hoy.month

    # Total facturación en el periodo (para gráfica de barras y KPI principal)
    total_facturacion = 0

    for f in FacturaEnergeticaTriple.objects.only('periodo', 'total_a_pagar'):
        if f.periodo and f.periodo.year == anio and f.periodo.month == mes:
            total_facturacion += float(f.total_a_pagar or 0)

    for f in FacturaPdbt.objects.only('periodo', 'total_a_pagar'):
        if f.periodo and f.periodo.year == anio and f.periodo.month == mes:
            total_facturacion += float(f.total_a_pagar or 0)


    # Facturación por UR en el periodo (para gráfica de barras y top UR)
    facturacion_por_ur = defaultdict(float)

    for f in FacturaEnergeticaTriple.objects.only('periodo', 'total_a_pagar', 'subestacion'):
        if f.periodo and f.periodo.year == anio and f.periodo.month == mes:
            ur = obtener_ur_desde_subestacion(f.subestacion)
            facturacion_por_ur[ur] += float(f.total_a_pagar or 0)

    for f in FacturaPdbt.objects.only('periodo', 'total_a_pagar', 'subestacion'):
        if f.periodo and f.periodo.year == anio and f.periodo.month == mes:
            ur = obtener_ur_desde_subestacion(f.subestacion)
            facturacion_por_ur[ur] += float(f.total_a_pagar or 0)


    # UR con mayor facturación en el periodo
    top_ur_facturacion = max(
        facturacion_por_ur.items(),
        key=lambda x: x[1],
        default=("Sin datos", 0)
    )

    ur_top_nombre = top_ur_facturacion[0]
    ur_top_monto = top_ur_facturacion[1]

    # 5. Infraestructura: cantidad de edificios, áreas, subestaciones y periodos activos
    total_edificios = Edificio.objects.count()
    total_areas = Area.objects.count()
    total_subestaciones = Subestacion.objects.count()
    periodos_activos = PeriodoInventario.objects(status="Activo").count()

    # 6. Metricas adicionales: consumo por UR, consumo por edificio, cantidad de equipos por área
    consumo_por_ur = defaultdict(float)
    consumo_por_edificio = defaultdict(float)
    equipos_por_area = defaultdict(int)

    modelos = [InventarioClimatizacion, InventarioLuminarias, InventarioMiscelaneos]

    for model in modelos:
        for item in model.objects.only('consumo_mensual', 'unidad_responsable', 'edificio', 'area'):
            
            if item.unidad_responsable:
                consumo_por_ur[str(item.unidad_responsable.nombre)] += float(item.consumo_mensual or 0)

            if item.edificio:
                consumo_por_edificio[str(item.edificio.nombre)] += float(item.consumo_mensual or 0)

            if item.area:
                equipos_por_area[str(item.area.nombre)] += 1

    top_ur = max(consumo_por_ur.items(), key=lambda x: x[1], default=("N/A", 0))
    top_edificio = max(consumo_por_edificio.items(), key=lambda x: x[1], default=("N/A", 0))
    top_area = max(equipos_por_area.items(), key=lambda x: x[1], default=("N/A", 0))

    # 7. Funciones auxiliares para procesar datos de facturas
    def parse_periodo(periodo_str):
        """Convierte string de periodo a datetime"""
        try:
            return datetime.strptime(periodo_str, "%Y-%m")
        except:
            try:
                return datetime.strptime(periodo_str, "%b-%Y")
            except:
                return None

    def obtener_ur_desde_subestacion(sub):
        """Obtiene nombre de UR desde subestación"""
        try:
            return sub.unidad_responsable.nombre if sub and sub.unidad_responsable else "Sin UR"
        except:
            return "Sin UR"

    # 8. Consumo total por mes (para gráfica de barras)
    consumo_mensual = defaultdict(float)

    for f in FacturaEnergeticaTriple.objects.only('periodo', 'consumo'):
        fecha = parse_periodo(f.periodo)
        if fecha:
            consumo_mensual[fecha.strftime("%Y-%m")] += float(f.consumo or 0)

    for f in FacturaPdbt.objects.only('periodo', 'consumo'):
        fecha = parse_periodo(f.periodo)
        if fecha:
            consumo_mensual[fecha.strftime("%Y-%m")] += float(f.consumo or 0)

    consumo_ordenado = dict(sorted(consumo_mensual.items()))
    periodos = list(consumo_ordenado.keys())
    consumos = list(consumo_ordenado.values())

    # 9. Consumo por tipo de tarifa a lo largo del tiempo (series para gráfica lineal)
    consumo_tarifa = {
        "GDMTH": defaultdict(float),
        "GDMTO": defaultdict(float),
        "GDBT": defaultdict(float),
        "PDBT": defaultdict(float),
    }

    for f in FacturaEnergeticaTriple.objects.only('periodo', 'consumo', 'tipo_tarifa'):
        fecha = parse_periodo(f.periodo)
        if fecha:
            key = fecha.strftime("%Y-%m")
            consumo_tarifa[f.tipo_tarifa][key] += float(f.consumo or 0)

    for f in FacturaPdbt.objects.only('periodo', 'consumo'):
        fecha = parse_periodo(f.periodo)
        if fecha:
            consumo_tarifa["PDBT"][fecha.strftime("%Y-%m")] += float(f.consumo or 0)

    # 10. Consumo por UR a lo largo del tiempo (series para gráfica lineal)
    consumo_por_ur_periodo = defaultdict(lambda: defaultdict(float))
    todos_periodos = set()

    for f in FacturaEnergeticaTriple.objects.only('periodo', 'consumo', 'subestacion'):
        fecha = parse_periodo(f.periodo)
        if fecha:
            p = fecha.strftime("%Y-%m")
            ur = obtener_ur_desde_subestacion(f.subestacion)
            consumo_por_ur_periodo[ur][p] += float(f.consumo or 0)
            todos_periodos.add(p)

    for f in FacturaPdbt.objects.only('periodo', 'consumo', 'subestacion'):
        fecha = parse_periodo(f.periodo)
        if fecha:
            p = fecha.strftime("%Y-%m")
            ur = obtener_ur_desde_subestacion(f.subestacion)
            consumo_por_ur_periodo[ur][p] += float(f.consumo or 0)
            todos_periodos.add(p)

    periodos_ordenados = sorted(list(todos_periodos))

    series_ur = []
    for ur, datos in consumo_por_ur_periodo.items():
        series_ur.append({
            "name": ur,
            "type": "line",
            "smooth": True,
            "data": [datos.get(p, 0) for p in periodos_ordenados]
        })

    # 11. Consumo vs costo
    clima_data = [120, 132, 101, 134, 90]
    lum_data = [220, 182, 191, 234, 290]
    misc_data = [150, 232, 201, 154, 190]

    # 12. Grafica donut por UR con más registros en inventario (clima, luminarias, miscelaneos)
    from collections import Counter

    conteo_ur_total = Counter()
    detalle_ur = defaultdict(lambda: {
        "clima": 0,
        "luminarias": 0,
        "miscelaneos": 0
    })

    # -------- CONTAR REGISTROS POR UR Y TIPO --------
    for item in InventarioClimatizacion.objects.only('unidad_responsable'):
        if item.unidad_responsable:
            ur = str(item.unidad_responsable.nombre)
            conteo_ur_total[ur] += 1
            detalle_ur[ur]["clima"] += 1

    for item in InventarioLuminarias.objects.only('unidad_responsable'):
        if item.unidad_responsable:
            ur = str(item.unidad_responsable.nombre)
            conteo_ur_total[ur] += 1
            detalle_ur[ur]["luminarias"] += 1

    for item in InventarioMiscelaneos.objects.only('unidad_responsable'):
        if item.unidad_responsable:
            ur = str(item.unidad_responsable.nombre)
            conteo_ur_total[ur] += 1
            detalle_ur[ur]["miscelaneos"] += 1

    # -------- OBTENER UR CON MÁS REGISTROS --------
    top_ur_registros = conteo_ur_total.most_common(1)

    if top_ur_registros:
        ur_nombre = top_ur_registros[0][0]
        datos_ur = detalle_ur[ur_nombre]
    else:
        ur_nombre = "Sin datos"
        datos_ur = {"clima": 0, "luminarias": 0, "miscelaneos": 0}

    # -------- FORMATO PARA ECHART --------
    donut_ur_data = [
        {"value": datos_ur["clima"], "name": "Climatización"},
        {"value": datos_ur["luminarias"], "name": "Luminarias"},
        {"value": datos_ur["miscelaneos"], "name": "Misceláneos"},
    ]


    # 13. Gráfica consumo vs costo (datos por mes del año seleccionado)

    anio_seleccionado = request.GET.get("anio")

    datos_por_anio = defaultdict(lambda: {
        "consumo": [0]*12,
        "costo": [0]*12
    })

    # Factura Triple
    for f in FacturaEnergeticaTriple.objects.only('periodo', 'consumo', 'total_a_pagar'):
        
        if not f.periodo:
            continue

        anio = str(f.periodo.year)
        mes_index = f.periodo.month - 1  # 0–11

        datos_por_anio[anio]["consumo"][mes_index] += float(f.consumo or 0)
        datos_por_anio[anio]["costo"][mes_index] += float(f.total_a_pagar or 0)


    # Factura PDBT
    for f in FacturaPdbt.objects.only('periodo', 'consumo', 'total_a_pagar'):
        
        if not f.periodo:
            continue

        anio = str(f.periodo.year)
        mes_index = f.periodo.month - 1

        datos_por_anio[anio]["consumo"][mes_index] += float(f.consumo or 0)
        datos_por_anio[anio]["costo"][mes_index] += float(f.total_a_pagar or 0)

    # AÑos disponibles para el selector
    anios_disponibles = sorted(datos_por_anio.keys())

    # Año seleccionado válido
    if not anio_seleccionado or anio_seleccionado not in datos_por_anio:
        anio_seleccionado = anios_disponibles[-1] if anios_disponibles else None


    # Datos para la gráfica lineal (consumo vs costo) del año seleccionado
    if anio_seleccionado:
        consumo_data = datos_por_anio[anio_seleccionado]["consumo"]
        costo_data = datos_por_anio[anio_seleccionado]["costo"]
    else:
        consumo_data = [0]*12
        costo_data = [0]*12


    # Labels de meses para la gráfica
    meses_labels = [
        "Ene", "Feb", "Mar", "Abr", "May", "Jun",
        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
    ]

    # 14. Contexto para renderizar plantilla

    import json

    context = {
        # Usuario
        "primer_nombre": primer_nombre,

        # Inventario
        "total_clima": total_clima,
        "total_lum": total_lum,
        "total_misc": total_misc,
        "total_equipos": total_equipos,

        # Consumo
        "consumo_clima": consumo_clima,
        "consumo_lum": consumo_lum,
        "consumo_misc": consumo_misc,
        "consumo_total": consumo_total,
        "consumo_promedio": consumo_promedio,

        # Facturación
        "pagadas": pagadas,
        "no_pagadas": no_pagadas,
        "porcentaje_pago": porcentaje_pago,
        "total_facturacion": total_facturacion,
        "ur_top_nombre_facturacion": ur_top_nombre,
        "ur_top_monto": ur_top_monto,

        # Infraestructura
        "total_edificios": total_edificios,
        "total_areas": total_areas,
        "total_subestaciones": total_subestaciones,
        "periodos_activos": periodos_activos,

        # Tops
        "top_ur": top_ur[0],
        "top_ur_consumo": top_ur[1],
        "top_edificio": top_edificio[0],
        "top_edificio_consumo": top_edificio[1],
        "top_area": top_area[0],
        "top_area_equipos": top_area[1],

        # Gráficas
        "periodos": periodos,
        "consumos": consumos,
        "clima_data": clima_data,
        "lum_data": lum_data,
        "misc_data": misc_data,

        # Series avanzadas
        "periodos_ur": json.dumps(periodos_ordenados),
        "series_ur": json.dumps(series_ur),

        # Donut UR
        "ur_top_nombre": ur_nombre,
        "donut_ur_data": json.dumps(donut_ur_data),

        # Consumo vs Costo
        "meses_labels": json.dumps(meses_labels),
        "consumo_data": json.dumps(consumo_data),
        "costo_data": json.dumps(costo_data),
        "anios_disponibles": anios_disponibles,
        "anio_actual": anio_seleccionado,
    }

    return render(request, 'systemsigo/index.html', context)
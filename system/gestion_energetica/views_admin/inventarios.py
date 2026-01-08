from bson import ObjectId

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

from mongoengine.errors import DoesNotExist

from system.models import InventarioClimatizacion, InventarioLuminarias, InventarioMiscelaneos, PeriodoInventario, UnidadResponsable
from system.views import get_user
from system.decorators import login_required_custom

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Border, Side, Alignment, PatternFill

@never_cache
@login_required_custom
def historiales_registros_inventarios_admin(request):
    return render(request, 'systemsigo/Inventarios/historiales.html')  

@never_cache
@login_required_custom
def admin_inventarios_filtro(request):
    """
    Vista para filtrar y listar inventarios según unidad responsable, periodo y tipo.
    - Restringida a usuarios autenticados con el decorador login_required_custom.
    - never_cache: evita el almacenamiento en caché de esta vista.
    - Calcula totales de potencia, horas y consumo según el tipo seleccionado.
    - Muestra un formulario de filtro y los resultados en la misma página.
    - Si el usuario no es admin, redirige al login con un mensaje de error.
    """

    user = get_user(request)
    if not user or user.rol not in ["admin", "admin_energia", "admin_ambiental"]:
        messages.error(request, "Acceso denegado.")
        return redirect("login")

    unidades = UnidadResponsable.objects()
    periodos = PeriodoInventario.objects()
    tipos = ["Climatización", "Luminarias", "Misceláneos"]

    # Inicializar variables de totales
    total_potencia_clim = total_horas_clim = total_consumo_clim = 0
    total_potencia_lum = total_horas_lum = total_consumo_lum = 0
    total_potencia_misc = total_horas_misc = total_consumo_misc = 0

    registros = []
    unidad_id = request.GET.get("unidad")
    periodo_id = request.GET.get("periodo")
    tipo = request.GET.get("tipo")

    if unidad_id and periodo_id and tipo:
        try:
            unidad_obj = UnidadResponsable.objects.get(id=ObjectId(unidad_id))
            periodo_obj = PeriodoInventario.objects.get(id=ObjectId(periodo_id))

            modelo_map = {
                "Climatización": InventarioClimatizacion,
                "Luminarias": InventarioLuminarias,
                "Misceláneos": InventarioMiscelaneos
            }

            modelo = modelo_map.get(tipo)
            if modelo:
                registros = modelo.objects(
                    unidad_responsable=unidad_obj,
                    periodo=periodo_obj
                )

                # Calcular totales según tipo
                if tipo == "Climatización":
                    total_potencia_clim = sum([i.potencia_total or 0 for i in registros])
                    total_horas_clim = sum([i.horas_mes or 0 for i in registros])
                    total_consumo_clim = sum([i.consumo_mensual or 0 for i in registros])

                elif tipo == "Luminarias":
                    total_potencia_lum = sum([i.potencia_total_lum or 0 for i in registros])
                    total_horas_lum = sum([i.consumo_mensual_horas or 0 for i in registros])
                    total_consumo_lum = sum([i.consumo_mensual or 0 for i in registros])

                elif tipo == "Misceláneos":
                    total_potencia_misc = sum([i.potencia_total or 0 for i in registros])
                    total_horas_misc = sum([i.horas_mes or 0 for i in registros])
                    total_consumo_misc = sum([i.consumo_mensual or 0 for i in registros])

        except Exception as e:
            messages.error(request, f"Error al obtener registros: {e}")

    return render(request, "systemsigo/Inventarios/lista.html", {
        "unidades": unidades,
        "periodos": periodos,
        "tipos": tipos,
        "registros": registros,
        "unidad_seleccionada": unidad_id,
        "periodo_seleccionado": periodo_id,
        "tipo_seleccionado": tipo,
        "total_potencia_clim": total_potencia_clim,
        "total_consumo_clim": total_consumo_clim,
        "total_horas_clim": total_horas_clim,
        "total_potencia_lum": total_potencia_lum,
        "total_horas_lum": total_horas_lum,
        "total_consumo_lum": total_consumo_lum,
        "total_potencia_misc": total_potencia_misc,
        "total_horas_misc": total_horas_misc,
        "total_consumo_misc": total_consumo_misc
    })

@never_cache
@login_required_custom
def exportar_excel_inventario(request):
    """
    Vista para exportar los inventarios filtrados a un archivo Excel.
    - Restringida a usuarios autenticados con el decorador login_required_custom.
    - never_cache: evita el almacenamiento en caché de esta vista.
    - Genera un archivo Excel con los datos del inventario según la unidad, periodo y tipo seleccionados.
    - Los totales de potencia, horas y consumo se calculan y se incluyen en el archivo.
    - El archivo se descarga automáticamente con un nombre basado en la unidad y periodo seleccionados.
    - Si no se encuentra la unidad o periodo, muestra un mensaje de error y redirige a la vista de filtro.
    """

    unidad_id = request.GET.get('unidad')
    periodo_id = request.GET.get('periodo')
    tipo = request.GET.get('tipo')

    try:
        unidad = UnidadResponsable.objects.get(id=unidad_id)
    except DoesNotExist:
        messages.error(request, "Unidad responsable no encontrada.")
        return redirect("admin_inventarios_filtro")

    try:
        periodo = PeriodoInventario.objects.get(id=periodo_id)
    except DoesNotExist:
        messages.error(request, "Periodo no encontrado.")
        return redirect("admin_inventarios_filtro")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{tipo}"

    total_potencia = 0
    total_consumo = 0
    total_horas_mes = 0  # si aplica

    if tipo == "Climatización":
        headers = [
            "Edificio", "Nivel", "Área", "Tipo Clima", "Marca", "Modelo", "Capacidad BTU/HR",
            "Voltaje", "Amperaje", "Potencia (W)", "Potencia total (Kw)", "Horas al mes", "Consumo mensual",
            "Fecha de registro", "Creado por", "Actualizado por", "Última modificación"
        ]
        registros = InventarioClimatizacion.objects.filter(unidad_responsable=unidad, periodo=periodo)
        data = []
        for i in registros:
            total_potencia += i.potencia_total or 0
            total_horas_mes += i.horas_mes or 0
            total_consumo += i.consumo_mensual or 0
            data.append([
                i.edificio.nombre, i.nivel, i.area.nombre, i.tipo_clima, i.marca, i.modelo,
                i.capacidad, i.voltaje, i.amperaje, i.potencia, i.potencia_total, i.horas_mes, i.consumo_mensual,
                i.fecha_registro.strftime('%Y-%m-%d %H:%M') if i.fecha_registro else '',
                i.creado_por.nombre_completo if i.creado_por else '',
                i.actualizado_por.nombre_completo if i.actualizado_por else '',
                i.ultima_actualizacion.strftime('%Y-%m-%d %H:%M') if i.ultima_actualizacion else ''
            ])

    elif tipo == "Luminarias":
        headers = [
            "Edificio", "Área", "Nivel", "Tipo Lámpara", "N° Luminarias", "Lámparas/Luminaria",
            "Potencia por lámpara", "Potencia Total", "Horas al mes", "Consumo mensual", "Fecha de registro",
            "Creado por", "Actualizado por", "Última modificación"
        ]
        registros = InventarioLuminarias.objects.filter(unidad_responsable=unidad, periodo=periodo)
        data = []
        for i in registros:
            total_potencia += i.potencia_total_lum or 0
            total_horas_mes += i.consumo_mensual_horas or 0
            total_consumo += i.consumo_mensual or 0
            data.append([
                i.edificio.nombre, i.area.nombre, i.nivel, i.tipo_lampara, i.num_luminarias,
                i.lamp_luminarias, i.potencia_lamp, i.potencia_total_lum, i.consumo_mensual_horas, i.consumo_mensual,
                i.fecha_registro.strftime('%Y-%m-%d %H:%M') if i.fecha_registro else '',
                f"{i.creado_por.nombre_completo} ({i.creado_por.email})" if i.creado_por else "N/A",
                f"{i.actualizado_por.nombre_completo} ({i.actualizado_por.email})" if i.actualizado_por else "N/A",
                i.ultima_actualizacion.strftime('%Y-%m-%d %H:%M') if i.ultima_actualizacion else "N/A"
            ])

    elif tipo == "Misceláneos":
        headers = [
            "Edificio", "Nivel", "Área", "Misceláneo", "Marca", "Modelo", "Voltaje", "Amperaje",
            "Potencia", "Horas al mes", "Consumo mensual", "Fecha de registro", "Creado por", "Actualizado por", "Última modificación"
        ]
        registros = InventarioMiscelaneos.objects.filter(unidad_responsable=unidad, periodo=periodo)
        data = []
        for i in registros:
            total_potencia += i.potencia or 0
            total_horas_mes += i.horas_mes or 0
            total_consumo += i.consumo_mensual or 0
            data.append([
                i.edificio.nombre, i.nivel, i.area.nombre, i.miscelaneos, i.marca, i.modelo,
                i.voltaje, i.amperaje, i.potencia, i.horas_mes, i.consumo_mensual,
                i.fecha_registro.strftime('%Y-%m-%d %H:%M') if i.fecha_registro else '',
                f"{i.creado_por.nombre_completo} ({i.creado_por.email})" if i.creado_por else "N/A",
                f"{i.actualizado_por.nombre_completo} ({i.actualizado_por.email})" if i.actualizado_por else "N/A",
                i.ultima_actualizacion.strftime('%Y-%m-%d %H:%M') if i.ultima_actualizacion else "N/A"
            ])
    else:
        return HttpResponse("Tipo no válido", status=400)

    # Escribir cabecera con estilo
    ws.append(headers)
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="305496", end_color="305496", fill_type="solid")
    border = Border(left=Side(style='thin'), right=Side(style='thin'),
                    top=Side(style='thin'), bottom=Side(style='thin'))

    for col_num, col in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center")

    # Escribir datos
    for row in data:
        ws.append(row)

    # Escribir totales (última fila)
    total_row = [""] * len(headers)
    if tipo == "Climatización":
        total_row[10] = total_potencia  # Potencia total (Kw)
        total_row[11] = total_horas_mes
        total_row[12] = total_consumo  # Consumo mensual
    elif tipo == "Luminarias":
        total_row[7] = total_potencia
        total_row[8] = total_horas_mes
        total_row[9] = total_consumo
    elif tipo == "Misceláneos":
        total_row[8] = total_potencia
        total_row[9] = total_horas_mes
        total_row[10] = total_consumo

    ws.append(total_row)

    # Estilo para fila de totales
    total_font = Font(bold=True)
    last_row_idx = ws.max_row
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=last_row_idx, column=col)
        cell.font = total_font
        cell.border = border

    # Ajustar ancho de columnas automáticamente
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2

    # Preparar respuesta
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    nombre_archivo = f"Inventario_{tipo}_{unidad.nombre}_{periodo.nombre}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    wb.save(response)
    return response
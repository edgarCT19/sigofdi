from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
# ==================== Vistas de Administrador del Sistema ====================
from .gestion_energetica.views_admin.index import Inicio
from .gestion_energetica.views_admin.campus import listar_campus, crear_campus, editar_campus, eliminar_campus
from .gestion_energetica.views_admin.unidades_responsables import listar_unidades, crear_unidad, editar_unidad, eliminar_unidad
from .gestion_energetica.views_admin.edificios import listar_edificios_admin
from .gestion_energetica.views_admin.usuarios import (
    User_List, Add_User, Edit_User, Delete_User, usuarios_inactivos,
    reactivar_usuario, eliminar_permanente)
from .gestion_energetica.views_admin.tarifas import (
    lista_tarifas, crear_tarifa, editar_tarifa, eliminar_tarifa)
from .gestion_energetica.views_admin.areas import listar_areas_admin
from .gestion_energetica.views_admin.subestacion import (subestaciones_admin, registrar_subestacion_admin,
                                                         editar_subestacion_admin, eliminar_subestacion_admin)
from .gestion_energetica.views_admin.facturas import (
    listar_facturas_admin, exportar_facturas_pdbt_excel_admin,
    exportar_facturas_triple_excel_admin, crear_factura_triple,
    api_subestaciones_por_ur, editar_factura_triple_admin,
    eliminar_factura_triple_admin, crear_factura_pdbt,
    editar_factura_pdbt_admin, eliminar_factura_pdbt_admin, listar_facturas_pdbt_admin, listar_facturas_triple_admin)
from .gestion_energetica.views_admin.inventarios import admin_inventarios_filtro, exportar_excel_inventario

from .gestion_energetica.views_admin.inventario_climatizacion import ( listado_inventario_climatizacion, 
    registrar_inventario_climatizacion_admin, editar_inventario_climatizacion_admin, eliminar_inventario_climatizacion_admin)
from .gestion_energetica.views_admin.inventario_luminarias import ( listado_inventario_luminarias_admin, 
    registrar_inventario_luminarias_admin, editar_inventario_luminarias_admin, eliminar_inventario_luminarias_admin)
from .gestion_energetica.views_admin.inventario_miscelaneos import ( listado_inventario_miscelaneos, 
    registrar_inventario_miscelaneos_admin, editar_inventario_miscelaneos_admin, eliminar_inventario_miscelaneos_admin)

from .gestion_energetica.views_admin.inventarios import historiales_registros_inventarios_admin

from .gestion_energetica.views_admin.historial_climas import (historial_climatizacion_admin, dar_baja_inventario_climatizacion,
    registro_climatizacion_bajas_admin, restaurar_registro_climatizacion)  

from .gestion_energetica.views_admin.historial_lum import (historial_luminarias_admin, dar_baja_luminaria, restaurar_registro_luminaria)

from .gestion_energetica.views_admin.historial_misc import (historial_miscelaneos_admin, dar_baja_miscelaneo_admin, 
                                                            restaurar_miscelaneo_admin)

from .gestion_energetica.views_admin.periodos_inventarios import (
    crear_periodo_inventario, listar_periodos, editar_periodo_inventario,
    eliminar_periodo_inventario)
from .gestion_energetica.views_admin.area_edificio import (
    ajax_edificios_por_ur_admin, ajax_areas_por_ur_admin)
from .gestion_energetica.views_admin.medidores import (medidores_lista_admin,
    medidores_eliminar_admin, medidores_crear_admin, medidores_editar_admin)

# ==================== Vistas de Encargado de Unidad Responsable ====================
from .gestion_energetica.views_encargado_ur.index import Inicio_encargado
from .gestion_energetica.views_encargado_ur.edificios import (
    listar_edificios, alta_edificio, editar_edificio, eliminar_edificio)
from .gestion_energetica.views_encargado_ur.areas import lista_areas, agregar_areas, editar_areas, eliminar_areas
from .gestion_energetica.views_encargado_ur.usuarios_capturistas import (
    listar_capturistas, Add_Capturistas, Edit_Capturistas, Delete_Capturista)
from .gestion_energetica.views_encargado_ur.subestaciones import (
    registrar_subestacion, listar_subestaciones_encargado,
    editar_subestacion, eliminar_subestacion)
from .gestion_energetica.views_encargado_ur.facturas_triple import (
    registrar_factura_triple, listar_facturas_triple, descargar_pdf_factura,
    eliminar_factura_triple, editar_factura_triple, exportar_facturas_triple_excel)
from .gestion_energetica.views_encargado_ur.factura_pdbt import (
    listar_facturas_pdbt, registrar_factura_pdbt, editar_factura_pdbt,
    eliminar_factura_pdbt, descargar_pdf_factura_pdbt, exportar_facturas_pdbt_excel)
from .gestion_energetica.views_encargado_ur.inventario_listas import (
    listar_climatizacion_encargado, listar_luminarias_encargado,
    listar_miscelaneos_encargado)
# ==================== Vistas del Rector ====================
from .gestion_energetica.views_rector.index import Inicio_rector
# ==================== Vistas del Director ====================
from .gestion_energetica.views_director.index import Inicio_director
# ==================== Vistas del Capturista de Datos ====================
from .gestion_energetica.views_capturista.index import Inicio_capturista
from .gestion_energetica.views_capturista.inv_climatizacion import (
    registrar_inventario_climatizacion, obtener_areas_por_edificio,
    listar_inventario_climatizacion, editar_inventario_climatizacion,
    eliminar_inventario_climatizacion)
from .gestion_energetica.views_capturista.inv_luminarias import (
    registrar_inventario_luminarias, listar_inventario_luminarias,
    editar_inventario_luminarias, eliminar_inventario_luminarias,
    obtener_areas_luminarias)
from .gestion_energetica.views_capturista.inv_miscelaneos import (
    registrar_inventario_miscelaneos, listar_inventario_miscelaneos,
    editar_inventario_miscelaneos, eliminar_inventario_miscelaneos,
    obtener_areas_por_edificio_miscelaneos)
# ==================== Vistas del Auditor ====================
from .gestion_energetica.views_auditor.index import Inicio_auditor
# ==================== Vistas de Errores ====================
from .gestion_energetica.views_errores.index import error_edit
# ==================== Vista de inicio admin de energias ====================
from .gestion_energetica.views_admin.inicio_energia import inicio_energia



urlpatterns = [
    # ==================== Paths de Inicio de Sesión ====================
    path('', views.Login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Links de restauración de contraseña modulo interno
    path('cambiar-password/', views.SolicitarCambioPassword, name='cambiar_contrasena'),
    path('confirmar-cambio-password/', views.ConfirmarCambioPassword, name='confirmar_cambio_password'),
    # Links de restauración de contraseña modulo externo
    path('password-reset/', views.SolicitarRecuperacionPassword, name='solicitar_recuperacion'),
    path('password-reset/verificar/', views.VerificarCodigoResetPassword, name='verificar_codigo'),
    path('password-reset/cambiar/', views.CambiarPasswordReset, name='cambiar_password'),
    # Link del perfil de usuario
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('cambiar-foto/', views.cambiar_foto_perfil, name='cambiar_foto'),


    # ==================== Paths de Administrador ====================
    path('inicio/', Inicio, name='inicio'),

    #Links de los usuarios
    path('usuarios/', User_List, name='usuarios'),
    path('crear_usuario/', Add_User, name='crear_usuario'),
    path('usuarios/editar/<str:usuario_id>/', Edit_User, name='editar_usuario'),
    path('usuarios/eliminar/<str:usuario_id>/', Delete_User, name='eliminar_usuario'),
    # Links de usuarios inactivos
    path('usuarios/inactivos/', usuarios_inactivos, name='usuarios_inactivos'),
    path('usuarios/<str:usuario_id>/reactivar/', reactivar_usuario, name='reactivar_usuario'),
    path('usuarios/<str:usuario_id>/eliminar/', eliminar_permanente, name='eliminar_permanente'),
    # Links de tarifas
    path('tarifas/', lista_tarifas, name='lista_tarifas'),
    path('tarifas/crear/', crear_tarifa, name='crear_tarifa'),
    path('tarifas/editar/<str:tarifa_id>/', editar_tarifa, name='editar_tarifa'),
    path('tarifas/eliminar/<str:id>/', eliminar_tarifa, name='eliminar_tarifa'),
    # Link de Unidades Responsables
    path('unidades/', listar_unidades, name='listar_unidades'),
    path('unidades/crear/', crear_unidad, name='crear_unidad'),
    path('unidades/editar/<str:unidad_id>/', editar_unidad, name='editar_unidad'),
    path('unidades/eliminar/<str:unidad_id>/', eliminar_unidad, name='eliminar_unidad'),
    # Link de Campus
    path('campus/', listar_campus, name='listar_campus'),
    path('campus/crear/', crear_campus, name='crear_campus'),
    path('campus/editar/<str:campus_id>/', editar_campus, name='editar_campus'),
    path('campus/eliminar/<str:campus_id>/', eliminar_campus, name='eliminar_campus'),
    # Link de lista de edificios de ur del sistema
    path('todos_los_edificios/', listar_edificios_admin, name='todos_edificios'),
    # Link de lista de todas las areas del sistema
    path('todas_las_areas/', listar_areas_admin, name='todas_las_areas'),
    # Subestaciones de urs
    path('filtro/subestaciones/', subestaciones_admin, name='admin_subestaciones'),
    path('subestaciones/crear/', registrar_subestacion_admin, name='crear_subestacion_admin'),
    path('subestaciones/editar/admin/<str:id>/', editar_subestacion_admin, name='editar_subestacion_admin'),
    path('subestaciones/eliminar/admin/<str:id>/', eliminar_subestacion_admin, name='eliminar_subestacion_admin'),
    # Facturas 
    path('facturas/admin/', listar_facturas_admin, name='listar_facturas_admin'),
    path('facturas/admin/exportar/pdbt/', exportar_facturas_pdbt_excel_admin, name='exportar_facturas_pdbt_admin'),
    path('facturas/admin/exportar/triple/', exportar_facturas_triple_excel_admin, name='exportar_facturas_triple_admin'),
    path('facturas/triple/admin/', listar_facturas_triple_admin, name='listar_facturas_triple_admin'),
    path('facturas/crear/', crear_factura_triple, name='crear_factura'),
    path('api/subestaciones/<str:ur_id>/', api_subestaciones_por_ur, name='api_subestaciones_por_ur'),
    path('factura-triple/editar/<str:f_id>/', editar_factura_triple_admin, name='editar_factura_triple_admin'),
    path('factura-triple/eliminar/<str:f_id>/', eliminar_factura_triple_admin, name='eliminar_factura_triple_admin'),
    path('facturas/pdbt/admin/', listar_facturas_pdbt_admin, name='listar_facturas_pdbt_admin'),
    path("factura-pdbt/agregar/", crear_factura_pdbt, name="crear_factura_pdbt"),
    path("factura-pdbt/editar/<str:f_id>/", editar_factura_pdbt_admin, name="editar_factura_pdbt_admin"),
    path("factura-pdbt/eliminar/<str:f_id>/", eliminar_factura_pdbt_admin, name="eliminar_factura_pdbt_admin"),
    # Link de filttrado de datos para inventarios energeticos
    path("inventarios/filtro/triple/", admin_inventarios_filtro, name="inventarios_filtro_triple"),
    path('inventarios/exportar/', exportar_excel_inventario, name='exportar_excel_inventario'),
    # Links de captura de datos de inventarios energeticos (Climatizacion)
    path('listado/inventarios/climatizacion/', listado_inventario_climatizacion, name='listado_inventario_climatizacion'),
    path('inventario/climatizacion/agregar/', registrar_inventario_climatizacion_admin, name='registrar_inventario_climatizacion_admin'),
    path('inventario/climatizacion/admin/editar/<str:climatizacion_id>/', editar_inventario_climatizacion_admin, name='editar_inventario_climatizacion_admin'),
    path('inventario/climatizacion/admin/eliminar/<str:climatizacion_id>/', eliminar_inventario_climatizacion_admin, name='eliminar_inventario_climatizacion_admin'),
    # Links de captura de datos de inventarios energeticos (Luminarias)
    path('listado/inventarios/luminarias/', listado_inventario_luminarias_admin, name='listado_inventario_luminarias'),
    path('inventario/luminarias/agregar/', registrar_inventario_luminarias_admin, name='registrar_inventario_luminarias_admin'),
    path('inventario/luminarias/admin/editar/<str:luminarias_id>/', editar_inventario_luminarias_admin, name='editar_inventario_luminarias_admin'),
    path('inventario/luminarias/admin/eliminar/<str:luminarias_id>/', eliminar_inventario_luminarias_admin, name='eliminar_inventario_luminarias_admin'),
    # Links de captura de datos de inventarios energeticos (Miscelaneos)
    path('listado/inventarios/miscelaneos/', listado_inventario_miscelaneos, name='listado_inventario_miscelaneos'),
    path('inventario/miscelaneos/agregar/', registrar_inventario_miscelaneos_admin, name='registrar_inventario_miscelaneos_admin'),
    path('inventario/miscelaneos/admin/editar/<str:miscelaneos_id>/', editar_inventario_miscelaneos_admin, name='editar_inventario_miscelaneos_admin'),
    path('inventario/miscelaneos/admin/eliminar/<str:miscelaneos_id>/', eliminar_inventario_miscelaneos_admin, name='eliminar_inventario_miscelaneos_admin'),
    # Links de Ajax(Edificios y Areas)
    path('ajax/edificios/por_ur/', ajax_edificios_por_ur_admin, name='ajax_edificios_por_ur'),
    path('ajax/areas/por_ur/', ajax_areas_por_ur_admin, name='ajax_areas_por_ur'),
    # Links de historial de registros de inventarios
    path('historiales/inventarios/admin/', historiales_registros_inventarios_admin, name='historiales_registros_inventarios_admin'),
        # Links de historiales de inventarios energeticos (Aires Acondicionados)
    path('historiales/inventarios/climatizacion/admin/', historial_climatizacion_admin, name='historial_climatizacion_admin'),
    path('inventario/climatizacion/dar_baja/admin/<str:his_id>/', dar_baja_inventario_climatizacion, name='dar_baja_inventario_climatizacion'),
    path('inventario/climatizacion/registros_baja/admin/', registro_climatizacion_bajas_admin, name='registro_climatizacion_bajas_admin'),
    path('inventario/climatizacion/restaurar/<str:registro_id>/', restaurar_registro_climatizacion, name='restaurar_registro_climatizacion'),
        # Links de historiales de inventarios energeticos (Luminarias)
    path('historiales/inventarios/luminarias/admin/', historial_luminarias_admin, name='historial_luminarias_admin'),
    path('inventario/luminarias/dar_baja/admin/<str:id>/', dar_baja_luminaria, name='dar_baja_luminaria'),
    path('inventario/luminarias/restaurar/<str:id>/', restaurar_registro_luminaria, name='restaurar_registro_luminaria'),
        # Links de historiales de inventarios energeticos (Miscelaneos)
    path('historiales/inventarios/miscelaneos/admin/', historial_miscelaneos_admin, name='historial_miscelaneos_admin'),
    path('inventario/miscelaneos/dar_baja/admin/<str:id>/', dar_baja_miscelaneo_admin, name='dar_baja_miscelaneo_admin'),
    path('inventario/miscelaneos/restaurar/<str:id>/', restaurar_miscelaneo_admin, name='restaurar_miscelaneo_admin'),
    # Crear periodos de inventarios
    path('periodos/crear/', crear_periodo_inventario, name="crear_periodo_inventario"),
    path("periodos/", listar_periodos, name="listar_periodos"),
    path("periodos/editar/<id>/", editar_periodo_inventario, name="editar_periodo_inventario"),
    path("periodos/eliminar/<id>/", eliminar_periodo_inventario, name="eliminar_periodo_inventario"),
    # Links de medidores
    path('medidores/', medidores_lista_admin, name='medidores'),
    path('medidores/crear/', medidores_crear_admin, name='medidores_crear_admin'),
    path('medidores/editar/<str:id>/', medidores_editar_admin, name='medidores_editar_admin'),
    path('medidores/eliminar/<str:id>/', medidores_eliminar_admin, name='medidores_eliminar_admin'),
    # ==================== Paths de Admin de Energias ====================
    path('admin_energia/inicio/', inicio_energia, name='admin_energia_inicio'),
    # ==================== Paths de Rector ====================
    path('rector/', Inicio_rector, name='rector'),


    # ==================== Paths de Director ====================
    path('director/', Inicio_director, name='director'),


    # ==================== Paths de Encargado de UR ====================
    path('encargado_ur/', Inicio_encargado, name='encargado_ur'),
    # Links de edificios de encargado de ur
    path('lista_edificios/', listar_edificios, name='lista_edificios'),
    path('edificios/encargado/agregar/', alta_edificio, name='alta_edificio'),
    path('edificios/encargado/editar/<str:edificio_id>/', editar_edificio, name='editar_edificio'),
    path('edificios/encargado/eliminar/<str:edificio_id>/', eliminar_edificio, name='eliminar_edificio'),
    # Links para areas de edificios de las ur
    path('areas/', lista_areas, name='lista_areas'),
    path('areas/agregar/', agregar_areas, name='agregar_areas'),
    path('areas/editar/<str:area_id>/', editar_areas, name='editar_areas'),
    path('areas/eliminar/<str:area_id>/', eliminar_areas, name='eliminar_areas'),
    # Links de CRUD de usuarios capturistas
    path('lista_capturistas/', listar_capturistas, name='lista_capturistas'),
    path('usuarios/encargado/agregar/', Add_Capturistas, name='add_capturista_encargado'),
    path('usuarios/encargado/editar/<str:id>/', Edit_Capturistas, name='edit_capturista'),
    path('usuarios/eliminar/<str:id>/', Delete_Capturista, name='delete_capturista'),
    # Links de subestaciones para el encargado
    path('registrar/', registrar_subestacion, name='registrar_subestacion'),
    path('listar/', listar_subestaciones_encargado, name='listar_subestaciones_encargado'),
    path('editar/<str:id>/', editar_subestacion, name='editar_subestacion'),
    path('subestaciones/eliminar/<str:id>/', eliminar_subestacion, name='eliminar_subestacion'),
    # Links de registros de facturas
    path('facturas/triple/registrar/', registrar_factura_triple, name='registrar_factura_triple'),
    path('facturas/triple/', listar_facturas_triple, name='listar_facturas_triple'),
    path('facturas/triple/descargar/<str:factura_id>/', descargar_pdf_factura, name='descargar_pdf_factura'),
    path('facturas/triple/eliminar/<str:factura_id>/', eliminar_factura_triple, name='eliminar_factura_triple'),
    path('facturas/triple/editar/<str:factura_id>/', editar_factura_triple, name='editar_factura_triple'),
    # Para facturas triple (GDMTH, GDMTO, GDBT) descargar excel
    path('facturas/triple/exportar/', exportar_facturas_triple_excel, name='exportar_facturas_triple'),
    # Facturas PDBT
    path('facturas/pdbt/', listar_facturas_pdbt, name='listar_facturas_pdbt'),
    path('facturas/pdbt/agregar/', registrar_factura_pdbt, name='agregar_factura_pdbt'),
    path('facturas/pdbt/editar/<str:factura_id>/', editar_factura_pdbt, name='editar_factura_pdbt'),
    path('facturas/pdbt/eliminar/<str:factura_id>/', eliminar_factura_pdbt, name='eliminar_factura_pdbt'),
    path('facturas/pdbt/descargar/<str:factura_id>/', descargar_pdf_factura_pdbt, name='descargar_factura_pdbt'),
    path('facturas/pdbt/exportar/', exportar_facturas_pdbt_excel, name='exportar_facturas_pdbt'),
    # Links para el listado de datos de el encargado de ur de los inventarios
    path("encargado/inventario/climatizacion/", listar_climatizacion_encargado, name="listar_climatizacion_encargado"),
    path("encargado/inventario/luminarias/", listar_luminarias_encargado, name="listar_luminarias_encargado"),
    path("encargado/inventario/miscelaneos/", listar_miscelaneos_encargado, name="listar_miscelaneos_encargado"),


    # ==================== Paths de Capturista de datos ====================
    path('capturista/', Inicio_capturista, name='capturista'),
    # Links de Inventario energético de Aires Acondicionados
    path('inventario/climatizacion/agregar/cap/', registrar_inventario_climatizacion, name='registrar_inventario_climatizacion'),
    path('inventario/climatizacion/obtener_areas/', obtener_areas_por_edificio, name='obtener_areas_clima'),
    path('inventario/climatizacion/', listar_inventario_climatizacion, name='listar_inventario_climatizacion'),
    path('inventario/clima/editar/<str:id>/', editar_inventario_climatizacion, name='editar_inventario_climatizacion'),
    path('inventario/clima/eliminar/<str:id>/', eliminar_inventario_climatizacion, name='eliminar_inventario_climatizacion'),
    # Links de Inventario energético de Luminarias
    path('inventario/luminarias/', listar_inventario_luminarias, name='listar_inventario_luminarias'),
    path('inventario/luminarias/agregar/cap/', registrar_inventario_luminarias, name='registrar_inventario_luminarias'),
    path('inventario/luminarias/editar/<str:id>/', editar_inventario_luminarias, name='editar_inventario_luminarias'),
    path('inventario/luminarias/eliminar/<str:id>/', eliminar_inventario_luminarias, name='eliminar_inventario_luminarias'),
    path('inventario/luminarias/obtener_areas/', obtener_areas_luminarias, name='obtener_areas_luminarias'),
    # Links de Inventario energetico de Misceláneos
    path('inventario/miscelaneos/', listar_inventario_miscelaneos, name='listar_inventario_miscelaneos'),
    path('inventario/miscelaneos/agregar/cap/', registrar_inventario_miscelaneos, name='registrar_inventario_miscelaneos'),
    path('inventario/miscelaneos/editar/<str:id>/', editar_inventario_miscelaneos, name='editar_inventario_miscelaneos'),
    path('inventario/miscelaneos/eliminar/<str:id>/', eliminar_inventario_miscelaneos, name='eliminar_inventario_miscelaneos'),
    path('inventario/miscelaneos/obtener_areas/', obtener_areas_por_edificio_miscelaneos, name='obtener_areas_por_edificio_miscelaneos'),

    # ==================== Paths de Auditor ====================
    path('auditor/', Inicio_auditor, name='auditor'),


    # ==================== Paths de errores ====================
    path('error/', error_edit, name='error'),
    path('error/404/', views.error_404_view, name='error_404'),
    path('error/408/', views.error_408_view, name='error_408'),
    path('error/500/', views.error_500_view, name='error_500'),  
    path('mantenimiento_temporal/', views.error_503_view, name='mantenimiento_temporal'),
    path('error/504/', views.error_504_view, name='error_504'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
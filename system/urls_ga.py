from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
# Importar la vista bitacora_mensual_lista_admin
from .gestion_ambiental.views_admin.bitacora_mensual import (bitacora_mensual_lista_admin, 
    bitacora_mensual_crear_admin, bitacora_mensual_editar_admin, bitacora_mensual_eliminar_admin)
from .gestion_ambiental.views_admin.almacenamiento_temp import (almacenamiento_temporal_lista_admin, 
    almacenamiento_temporal_crear_admin, almacenamiento_temporal_editar_admin, almacenamiento_temporal_eliminar_admin)
from .gestion_ambiental.views_admin.bitacora_generacion import (bitacora_generacion_rpbi, 
    bitacora_rpbi_crear_admin, bitacora_rpbi_editar_admin, bitacora_rpbi_eliminar_admin)
from .gestion_ambiental.views_admin.bitacora_recoleccion import (bitacora_recoleccion_rpbi,
    bitacora_recoleccion_crear_admin, bitacora_recoleccion_editar_admin, bitacora_recoleccion_eliminar_admin)
from .gestion_ambiental.views_admin.vertedero_municipal import (vertedero_municipal_admin,
    vertedero_municipal_crear_admin, vertedero_municipal_editar_admin, vertedero_municipal_eliminar_admin)
from .gestion_ambiental.views_admin.centro_acopio_rme import (centro_de_acopio_rme_admin, 
    centro_acopio_rme_crear_admin, centro_acopio_rme_editar_admin, centro_acopio_rme_eliminar_admin)
from .gestion_ambiental.views_admin.centro_acopio_rrr import (centro_de_acopio_rrr_admin, 
    centro_acopio_rrr_crear_admin, centro_acopio_rrr_editar_admin, centro_acopio_rrr_eliminar_admin)
from .gestion_ambiental.views_admin.inicio_ambiental import inicio_ambiental

urlpatterns = [
    # ========================== Paths de Administrador ========================
    path('admin_ambiental/inicio/', inicio_ambiental, name='admin_ambiental_inicio'),
    # Rutas de las bitacoras mensuales
    path('bitacora_mensual/', bitacora_mensual_lista_admin, name='bitacora_mensual_lista_admin'),
    path('bitacora_mensual/crear/', bitacora_mensual_crear_admin, name='bitacora_mensual_crear_admin'),
    path('bitacora_mensual/editar/<str:id>/', bitacora_mensual_editar_admin, name='bitacora_mensual_editar_admin'),
    path('bitacora_mensual/eliminar/<str:id>/', bitacora_mensual_eliminar_admin, name='bitacora_mensual_eliminar_admin'),
    # Rutas de las bitacoras mensuales
    path('almacenamiento_temporal/', almacenamiento_temporal_lista_admin, name='almacenamiento_temporal'),
    path('almacenamiento_temporal/crear/', almacenamiento_temporal_crear_admin, name='almacenamiento_temporal_crear_admin'),
    path('almacenamiento_temporal/editar/<str:id>/', almacenamiento_temporal_editar_admin, name='almacenamiento_temporal_editar_admin'),
    path('almacenamiento_temporal/eliminar/<str:id>/', almacenamiento_temporal_eliminar_admin, name='almacenamiento_temporal_eliminar_admin'),
    # Rutas de la bitacora de generacion RPBI
    path('bitacora_generacion_rpbi/', bitacora_generacion_rpbi, name='bitacora_generacion_rpbi'),
    path('bitacora_rpbi/crear/', bitacora_rpbi_crear_admin, name='bitacora_rpbi_crear_admin'),
    path('bitacora_rpbi/editar/<str:id>/', bitacora_rpbi_editar_admin, name='bitacora_rpbi_editar_admin'),
    path('bitacora_rpbi/eliminar/<str:id>/', bitacora_rpbi_eliminar_admin, name='bitacora_rpbi_eliminar_admin'),
    # Rutas de la bitacora de recoleccion RPBI
    path('bitacora_recoleccion_rpbi/', bitacora_recoleccion_rpbi, name='bitacora_recoleccion_rpbi'),
    path('bitacora_recoleccion/crear/', bitacora_recoleccion_crear_admin, name='bitacora_recoleccion_crear_admin'),
    path('bitacora_recoleccion/editar/<str:id>/', bitacora_recoleccion_editar_admin, name='bitacora_recoleccion_editar_admin'),
    path('bitacora_recoleccion/eliminar/<str:id>/', bitacora_recoleccion_eliminar_admin, name='bitacora_recoleccion_eliminar_admin'), 
    # Ruta del vertedero municipal
    path('vertedero_municipal/admin/', vertedero_municipal_admin, name='vertedero_municipal_admin'), 
    path('vertedero_municipal/crear/', vertedero_municipal_crear_admin, name='vertedero_municipal_crear_admin'),
    path('vertedero_municipal/editar/<str:id>/', vertedero_municipal_editar_admin, name='vertedero_municipal_editar_admin'),
    path('vertedero_municipal/eliminar/<str:id>/', vertedero_municipal_eliminar_admin, name='vertedero_municipal_eliminar_admin'), 
    # Ruta para centro de acopio RME 
    path('centro_acopio_rme/admin/', centro_de_acopio_rme_admin, name='centro_acopio_rme_admin'), 
    path('centro_acopio_rme/crear/', centro_acopio_rme_crear_admin, name='centro_acopio_rme_crear_admin'),
    path('centro_acopio_rme/editar/<str:id>/', centro_acopio_rme_editar_admin, name='centro_acopio_rme_editar_admin'),
    path('centro_acopio_rme/eliminar/<str:id>/', centro_acopio_rme_eliminar_admin, name='centro_acopio_rme_eliminar_admin'),
    # Ruta para centro de acopio RRR
    path('centro_acopio_rrr/admin/', centro_de_acopio_rrr_admin, name='centro_acopio_rrr_admin'),
    path('centro_acopio_rrr/crear/', centro_acopio_rrr_crear_admin, name='centro_acopio_rrr_crear_admin'),
    path('centro_acopio_rrr/editar/<str:id>/', centro_acopio_rrr_editar_admin, name='centro_acopio_rrr_editar_admin'),
    path('centro_acopio_rrr/eliminar/<str:id>/', centro_acopio_rrr_eliminar_admin, name='centro_acopio_rrr_eliminar_admin'),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
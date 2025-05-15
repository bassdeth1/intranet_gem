# /workspaces/intranet_gem/intranet_core/urls.py
from django.urls import path
from . import views # Asegúrate que esto importa tus vistas correctamente

app_name = 'intranet_core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),

    # Gestión de Archivos
    path('archivos/', views.carga_archivos_view, name='carga_archivos'),
    path('archivos/carpeta/<int:carpeta_id>/', views.carga_archivos_view, name='carga_archivos_carpeta'),
    path('archivos/ver/<int:archivo_id>/', views.ver_archivo_view, name='ver_archivo'),
    path('archivos/editar/<int:archivo_id>/', views.editar_archivo_view, name='editar_archivo'),

    # Formularios Dinámicos
    path('formularios/', views.formularios_view, name='formularios'),
    path('formularios/crear/', views.formulario_crear_view, name='formulario_crear'),
    path('formularios/<int:formulario_id>/disenar/', views.formulario_disenar_view, name='formulario_disenar'),
    path('formularios/<int:formulario_id>/llenar/', views.formulario_llenar_view, name='formulario_llenar'),
    path('formularios/<int:formulario_id>/respuestas/', views.formulario_respuestas_view, name='formulario_respuestas'),
    # path('formularios/<int:formulario_id>/editar/', views.formulario_editar_view, name='formulario_editar_config'),
    # path('formularios/<int:formulario_id>/eliminar/', views.formulario_eliminar_view, name='formulario_eliminar'),

    # Calendario de Actividades
    path('calendario/', views.calendario_view, name='calendario'),
    path('calendario/eventos.json/', views.calendario_eventos_json_view, name='calendario_eventos_json'),
    path('calendario/evento/crear/', views.evento_calendario_crear_view, name='evento_calendario_crear'),
    path('calendario/evento/<int:evento_id>/', views.evento_calendario_detalle_view, name='evento_calendario_detalle'),
    path('calendario/evento/<int:evento_id>/editar/', views.evento_calendario_editar_view, name='evento_calendario_editar'),
    path('calendario/evento/<int:evento_id>/eliminar/', views.evento_calendario_eliminar_view, name='evento_calendario_eliminar'),

    # Gestión de Responsabilidades (Tareas)
    path('responsabilidades/', views.responsabilidades_view, name='responsabilidades'),
    path('responsabilidades/crear/', views.tarea_crear_view, name='tarea_crear'),
    path('responsabilidades/<int:tarea_id>/', views.tarea_detalle_view, name='tarea_detalle'),
    path('responsabilidades/<int:tarea_id>/editar/', views.tarea_editar_view, name='tarea_editar'),
    path('responsabilidades/<int:tarea_id>/eliminar/', views.tarea_eliminar_view, name='tarea_eliminar'),

    # Directorio de Usuarios
    path('directorio/', views.directorio_view, name='directorio'),
    path('directorio/usuario/<str:username>/', views.directorio_usuario_detalle_view, name='directorio_usuario_detalle'),

    # Reserva de Recursos
    path('reservas/', views.reservas_view, name='reservas'),
    path('reservas/eventos.json/', views.reservas_eventos_json_view, name='reservas_eventos_json'),
    path('reservas/crear/', views.reserva_crear_view, name='reserva_crear'),
    path('reservas/crear/<int:recurso_id>/', views.reserva_crear_view, name='reserva_crear_para_recurso'),

    # Wiki
    path('wiki/', views.wiki_view, name='wiki'),
    path('wiki/crear/', views.wiki_crear_articulo_view, name='wiki_crear_articulo'),
    path('wiki/<slug:slug>/', views.wiki_articulo_detalle_view, name='wiki_articulo_detalle'),
    path('wiki/<slug:slug>/editar/', views.wiki_editar_articulo_view, name='wiki_editar_articulo'),
    path('wiki/<slug:slug>/eliminar/', views.wiki_eliminar_articulo_view, name='wiki_eliminar_articulo'),

    # Notificaciones
    path('notificaciones/', views.notificaciones_page_view, name='notificaciones_page'),
    path('notificaciones/marcar-leida/<int:notificacion_id>/', views.marcar_notificacion_leida_view, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas-leidas/', views.marcar_todas_notificaciones_leidas_view, name='marcar_todas_notificaciones_leidas'),

    # Perfil y Configuración de Usuario
    path('perfil/', views.perfil_view, name='perfil'),
    path('configuracion/', views.configuracion_view, name='configuracion'),

    # Gestión de Usuarios (Staff)
    path('gestion-usuarios/', views.usuarios_gestion_view, name='usuarios_gestion'),
    path('gestion-usuarios/<int:user_id>/editar/', views.usuario_gestion_editar_view, name='usuario_gestion_editar'),
]
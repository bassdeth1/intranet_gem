# Ubicación: /workspaces/intranet_gem/intranet_core/admin.py
from django.contrib import admin
from .models import Archivo, Carpeta, ArticuloWiki, Notificacion # Añadir ArticuloWiki y Notificacion

@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    list_display = ('nombre_descriptivo', 'nombre_original_archivo', 'fecha_subida', 'subido_por', 'carpeta')
    list_filter = ('fecha_subida', 'subido_por', 'carpeta')
    search_fields = ('nombre_descriptivo', 'nombre_original_archivo', 'subido_por__username', 'carpeta__nombre')
    readonly_fields = ('fecha_subida',) # 'nombre_original_archivo' si se setea siempre en save

    def save_model(self, request, obj, form, change):
        if not obj.subido_por_id:
            obj.subido_por = request.user
        # Para setear nombre_original_archivo si no se hizo en la vista/form al crear/editar
        if obj.archivo_subido and not obj.nombre_original_archivo:
             obj.nombre_original_archivo = obj.archivo_subido.name
        super().save_model(request, obj, form, change)

@admin.register(Carpeta)
class CarpetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'subido_por', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'subido_por')
    search_fields = ('nombre', 'subido_por__username')
    readonly_fields = ('fecha_creacion',)

@admin.register(ArticuloWiki)
class ArticuloWikiAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'actualizado_el', 'creado_el', 'slug')
    search_fields = ('titulo', 'contenido', 'autor__username')
    prepopulated_fields = {'slug': ('titulo',)}
    list_filter = ('actualizado_el', 'creado_el', 'autor')
    readonly_fields = ('creado_el', 'actualizado_el')

    def save_model(self, request, obj, form, change):
        if not change and not obj.autor_id and request.user.is_authenticated: # Solo al crear y si no tiene autor
            obj.autor = request.user
        super().save_model(request, obj, form, change)

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('destinatario', 'mensaje_corto', 'leida', 'fecha_creacion', 'url_destino')
    list_filter = ('leida', 'fecha_creacion', 'destinatario')
    search_fields = ('destinatario__username', 'mensaje')
    readonly_fields = ('fecha_creacion',)
    actions = ['marcar_como_leida', 'marcar_como_no_leida']

    def mensaje_corto(self, obj):
        return (obj.mensaje[:75] + '...') if len(obj.mensaje) > 75 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'

    def marcar_como_leida(self, request, queryset):
        queryset.update(leida=True)
    marcar_como_leida.short_description = "Marcar seleccionadas como leídas"

    def marcar_como_no_leida(self, request, queryset):
        queryset.update(leida=False)
    marcar_como_no_leida.short_description = "Marcar seleccionadas como no leídas"
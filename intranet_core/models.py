# intranet_core/models.py
import os
from django.db import models
from django.contrib.auth.models import User # Mantenido, aunque settings.AUTH_USER_MODEL es más flexible
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings # Importante para referenciar al modelo User de forma flexible

# --- Funciones Auxiliares ---
def user_directory_path(instance, filename):
    # instance.subido_por puede ser None si el usuario fue eliminado y se seteó a SET_NULL
    # o si el modelo es diferente y 'subido_por' no es el campo de usuario.
    # Ajustaremos para que sea más genérico o específico por modelo si es necesario.
    # Para el modelo Archivo, instance.subido_por es correcto.
    user_id_folder = "unknown_user"
    if hasattr(instance, 'subido_por') and instance.subido_por:
        user_id_folder = f"user_{instance.subido_por.id}"
    elif hasattr(instance, 'creado_por') and instance.creado_por: # Para otros modelos
        user_id_folder = f"user_{instance.creado_por.id}"
    elif hasattr(instance, 'usuario') and instance.usuario: # Para PerfilUsuario
        user_id_folder = f"user_{instance.usuario.id}"

    # Determinar la subcarpeta según el tipo de instancia para organizar mejor los archivos
    if isinstance(instance, Archivo):
        return f'archivos_gestionados/{user_id_folder}/{filename}'
    elif isinstance(instance, PerfilUsuario) and 'foto_perfil' in filename: # Asumiendo que filename se pasa desde el campo
        return f'perfiles_usuarios/{user_id_folder}/{filename}'
    # Añadir más condiciones para otros modelos que suban archivos si es necesario
    return f'uploads_generales/{user_id_folder}/{filename}'

# --- Modelos Existentes ---

class Carpeta(models.Model):
    nombre = models.CharField(max_length=100)
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carpetas_creadas')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    carpeta_padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcarpetas') # DESCOMENTAR O AÑADIR

    class Meta:
        # Ajustar unique_together si carpeta_padre se añade y debe ser único en ese contexto
        unique_together = ('nombre', 'subido_por', 'carpeta_padre')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Archivo(models.Model):
    nombre_descriptivo = models.CharField(
        max_length=255,
        help_text="Nombre descriptivo o título del archivo",
        default=''
    )
    archivo_subido = models.FileField(
        upload_to=user_directory_path, # Reutilizamos la función pero podría ser más específica
        verbose_name="Archivo",
        null=False,
        blank=False
    )
    nombre_original_archivo = models.CharField(max_length=255, default='')
    fecha_subida = models.DateTimeField(default=timezone.now)
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='archivos_subidos')
    carpeta = models.ForeignKey(
        Carpeta,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='archivos_contenidos'
    )

    def __str__(self):
        return self.nombre_descriptivo or self.nombre_original_archivo

    def delete(self, *args, **kwargs):
        if self.archivo_subido and hasattr(self.archivo_subido, 'path'):
            file_path = self.archivo_subido.path
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error al eliminar el archivo físico {file_path}: {e}")
            else:
                print(f"Advertencia: El archivo físico no se encontró en {file_path} para el objeto Archivo ID {self.id}")
        super().delete(*args, **kwargs)

    def get_file_extension(self):
        if self.archivo_subido and self.archivo_subido.name:
            name, extension = os.path.splitext(self.archivo_subido.name)
            return extension.lower()
        return ''

    def is_viewable_in_browser(self):
        viewable_extensions = [
            '.txt', '.md', '.py', '.js', '.json', '.css', '.html', '.xml',
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',
            '.pdf'
        ]
        return self.get_file_extension() in viewable_extensions

    def get_view_url(self):
        return reverse('intranet_core:ver_archivo', args=[self.id])

    def get_edit_url(self):
        return reverse('intranet_core:editar_archivo', args=[self.id])

class ArticuloWiki(models.Model):
    titulo = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Dejar en blanco para autogenerar o especificar uno.")
    contenido = models.TextField(help_text="Contenido del artículo en formato Markdown.")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='articulos_wiki')
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-actualizado_el', 'titulo']
        verbose_name = "Artículo de Wiki"
        verbose_name_plural = "Artículos de Wiki"

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        original_slug_base = slugify(self.titulo)
        if not self.slug or (hasattr(self, '_original_titulo') and self._original_titulo != self.titulo and self.slug == slugify(self._original_titulo)):
            self.slug = original_slug_base

        final_slug = self.slug
        counter = 1
        while ArticuloWiki.objects.filter(slug=final_slug).exclude(pk=self.pk).exists():
            final_slug = f"{original_slug_base}-{counter}"
            counter += 1
        self.slug = final_slug
        
        self._original_titulo = self.titulo
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('intranet_core:wiki_articulo_detalle', kwargs={'slug': self.slug})

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._original_titulo = instance.titulo
        return instance

class Notificacion(models.Model):
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    url_destino = models.URLField(blank=True, null=True, help_text="URL opcional a la que se dirigirá al hacer clic.")
    # tipo_notificacion = models.CharField(max_length=50, blank=True, null=True) # Opcional para categorizar

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"Notificación para {self.destinatario.username}: {self.mensaje[:50]}"

# --- Nuevos Modelos para Funcionalidades Faltantes ---

# 1. Modelos para el Módulo de Formularios
class Formulario(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='formularios_creados')
    creado_el = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    fecha_limite = models.DateTimeField(blank=True, null=True, help_text="Opcional: Fecha y hora límite para enviar respuestas.")

    class Meta:
        verbose_name = "Formulario"
        verbose_name_plural = "Formularios"
        ordering = ['-creado_el']

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        # Intenta ser muy explícito aquí.
        # Asegúrate que el nombre de la app en intranet_core/urls.py es 'intranet_core'
        # y el nombre del path es 'formulario_llenar'.
        return reverse('intranet_core:formulario_llenar', kwargs={'formulario_id': self.pk}) # Usar self.pk es más idiomático que self.id

class CampoFormulario(models.Model):
    class TipoCampo(models.TextChoices):
        TEXTO_CORTO = 'TEXTO_CORTO', 'Texto Corto'
        TEXTO_LARGO = 'TEXTO_LARGO', 'Texto Largo (Área de texto)'
        NUMERO = 'NUMERO', 'Número'
        EMAIL = 'EMAIL', 'Correo Electrónico'
        FECHA = 'FECHA', 'Fecha'
        HORA = 'HORA', 'Hora'
        OPCION_MULTIPLE = 'OPCION_MULTIPLE', 'Opción Múltiple (una respuesta)'
        CASILLAS = 'CASILLAS', 'Casillas de Verificación (múltiples respuestas)'
        DESPLEGABLE = 'DESPLEGABLE', 'Desplegable (una respuesta)'
        ARCHIVO = 'ARCHIVO', 'Subir Archivo' # Considerar cómo manejar estos archivos
        # Separador/Texto informativo, etc.

    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name='campos')
    etiqueta = models.CharField(max_length=255, help_text="Pregunta o título del campo.")
    tipo_campo = models.CharField(max_length=50, choices=TipoCampo.choices)
    ayuda_texto = models.CharField(max_length=255, blank=True, null=True, help_text="Texto de ayuda o descripción adicional para el campo.")
    es_obligatorio = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0, help_text="Orden en que aparecerá el campo en el formulario.")
    opciones_choices = models.TextField(blank=True, null=True, help_text="Para campos de opción múltiple, casillas o desplegable. Ingrese las opciones separadas por un salto de línea (una opción por línea).")

    class Meta:
        verbose_name = "Campo de Formulario"
        verbose_name_plural = "Campos de Formularios"
        ordering = ['formulario', 'orden']

    def __str__(self):
        return f"{self.formulario.titulo} - {self.etiqueta} ({self.get_tipo_campo_display()})"

    def get_opciones_lista(self):
        if self.opciones_choices and self.tipo_campo in [self.TipoCampo.OPCION_MULTIPLE, self.TipoCampo.CASILLAS, self.TipoCampo.DESPLEGABLE]:
            return [opt.strip() for opt in self.opciones_choices.splitlines() if opt.strip()]
        return []

class RespuestaFormulario(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name='respuestas_recibidas')
    respondido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='respuestas_enviadas') # SET_NULL si el usuario es eliminado
    # ip_address = models.GenericIPAddressField(blank=True, null=True) # Si se permiten respuestas anónimas
    enviado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Respuesta de Formulario"
        verbose_name_plural = "Respuestas de Formularios"
        ordering = ['-enviado_el']

    def __str__(self):
        usuario = self.respondido_por.username if self.respondido_por else "Anónimo"
        return f"Respuesta de {usuario} para '{self.formulario.titulo}' el {self.enviado_el.strftime('%d/%m/%Y %H:%M')}"

class DatoRespuesta(models.Model):
    respuesta_formulario = models.ForeignKey(RespuestaFormulario, on_delete=models.CASCADE, related_name='datos')
    campo_formulario = models.ForeignKey(CampoFormulario, on_delete=models.CASCADE) # Considerar on_delete=models.PROTECT o SET_NULL si no se deben borrar datos si se borra un campo
    valor = models.TextField(blank=True) # Para múltiples opciones en casillas, se pueden guardar separadas por un delimitador especial
    # archivo_adjunto = models.FileField(upload_to='respuestas_formularios_archivos/', blank=True, null=True) # Si el campo es de tipo ARCHIVO

    class Meta:
        verbose_name = "Dato de Respuesta"
        verbose_name_plural = "Datos de Respuestas"

    def __str__(self):
        return f"Para '{self.campo_formulario.etiqueta}': {self.valor[:50]}"

# 2. Modelo para el Módulo de Calendario
class EventoCalendario(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True, help_text="Dejar en blanco si es un evento de día completo o sin duración específica en hora.")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='eventos_calendario')
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)
    # color_evento = models.CharField(max_length=7, blank=True, null=True, help_text="Color en formato hexadecimal, ej: #FF5733") # Para FullCalendar
    # recurrencia_regla = models.CharField(max_length=255, blank=True, null=True, help_text="Regla de recurrencia (ej. iCalendar RRULE)")
    # participantes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='eventos_participa')

    class Meta:
        verbose_name = "Evento de Calendario"
        verbose_name_plural = "Eventos de Calendario"
        ordering = ['fecha_inicio']

    def __str__(self):
        return self.titulo

# 3. Modelo para el Módulo de Responsabilidades (Gestión de Tareas)
class Tarea(models.Model):
    class EstadoTarea(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        EN_ESPERA = 'EN_ESPERA', 'En Espera'

    class PrioridadTarea(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGENTE', 'Urgente'

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_asignadas')
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tareas_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=EstadoTarea.choices, default=EstadoTarea.PENDIENTE)
    prioridad = models.CharField(max_length=10, choices=PrioridadTarea.choices, default=PrioridadTarea.MEDIA)
    # proyecto = models.ForeignKey('Proyecto', on_delete=models.SET_NULL, null=True, blank=True) # Si tienes un modelo Proyecto

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ['-prioridad', 'fecha_limite', 'fecha_creacion']

    def __str__(self):
        return self.titulo

# 4. Modelo para Perfil de Usuario (Opcional, para Directorio y Perfil)
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    departamento = models.CharField(max_length=100, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    telefono_extension = models.CharField(max_length=20, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to=user_directory_path, null=True, blank=True, default='perfiles_usuarios/default_avatar.png')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    biografia_corta = models.TextField(blank=True, null=True, help_text="Una breve descripción sobre ti.")


    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    # Podrías usar signals para crear PerfilUsuario automáticamente cuando se crea un User.
    # from django.db.models.signals import post_save
    # from django.dispatch import receiver
    # @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    # def create_or_update_user_profile(sender, instance, created, **kwargs):
    #     if created:
    #         PerfilUsuario.objects.create(usuario=instance)
    #     # instance.perfilusuario.save() # Si es una actualización y quieres guardar también el perfil

# 5. Modelos para Reserva de Recursos
class TipoRecurso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    icono_fa = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: 'fas fa-building', 'fas fa-desktop'") # Para mostrar un icono

    class Meta:
        verbose_name = "Tipo de Recurso"
        verbose_name_plural = "Tipos de Recursos"

    def __str__(self):
        return self.nombre

class Recurso(models.Model):
    nombre = models.CharField(max_length=100)
    tipo_recurso = models.ForeignKey(TipoRecurso, on_delete=models.PROTECT) # Evitar borrar tipo si hay recursos asociados
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    capacidad = models.PositiveIntegerField(blank=True, null=True, help_text="Ej: para salas de reuniones.")
    esta_activo = models.BooleanField(default=True, help_text="Indica si el recurso está disponible para ser reservado.")
    # responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario responsable del recurso.")
    # requiere_aprobacion = models.BooleanField(default=False, help_text="Si las reservas para este recurso necesitan aprobación.")


    class Meta:
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"
        ordering = ['tipo_recurso', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.tipo_recurso.nombre})"

class Reserva(models.Model):
    class EstadoReserva(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de Aprobación'
        APROBADA = 'APROBADA', 'Aprobada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        CANCELADA = 'CANCELADA', 'Cancelada por Usuario'

    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, related_name='reservas')
    reservado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mis_reservas')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    motivo = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=EstadoReserva.choices, default=EstadoReserva.APROBADA) # Cambiar si se implementa flujo de aprobación
    # aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas_aprobadas')
    # fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    creado_el = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['fecha_inicio']
        # unique_together = ('recurso', 'fecha_inicio', 'fecha_fin') # Considerar para evitar solapamientos a nivel BD, aunque es mejor validar en el form/view

    def __str__(self):
        return f"Reserva de '{self.recurso.nombre}' por {self.reservado_por.username} ({self.fecha_inicio.strftime('%d/%m %H:%M')} - {self.fecha_fin.strftime('%d/%m %H:%M')})"

    # Aquí podrías añadir un clean() method para validar que fecha_fin > fecha_inicio
    # y para validar solapamientos de reservas para el mismo recurso.
    # Ejemplo básico (se puede mejorar y hacer más robusto):
    # def clean(self):
    #     from django.core.exceptions import ValidationError
    #     if self.fecha_inicio and self.fecha_fin and self.fecha_inicio >= self.fecha_fin:
    #         raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
    #
    #     # Chequear solapamientos
    #     solapamientos = Reserva.objects.filter(
    #         recurso=self.recurso,
    #         fecha_inicio__lt=self.fecha_fin,
    #         fecha_fin__gt=self.fecha_inicio
    #     ).exclude(pk=self.pk) # Excluir la propia reserva si se está editando
    #
    #     if solapamientos.exists():
    #         raise ValidationError(f"El recurso '{self.recurso.nombre}' ya está reservado en el horario solicitado.")
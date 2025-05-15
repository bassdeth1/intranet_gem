# intranet_core/forms.py
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm

from .models import (
    Archivo, Carpeta, ArticuloWiki,
    Formulario, CampoFormulario, # Modelos de Formularios
    EventoCalendario, # Modelo de Calendario
    Tarea, # Modelo de Tareas/Responsabilidades
    PerfilUsuario, # Modelo de Perfil
    TipoRecurso, Recurso, Reserva # Modelos de Reservas
)

# Clases CSS comunes para los widgets de formulario para mantener la consistencia
COMMON_TEXT_INPUT_CLASSES = 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 shadow-sm focus:border-main-primary focus:ring-main-primary sm:text-sm'
COMMON_TEXTAREA_CLASSES = COMMON_TEXT_INPUT_CLASSES + ' min-h-[100px]' # Añadir altura mínima
COMMON_SELECT_CLASSES = COMMON_TEXT_INPUT_CLASSES
COMMON_FILE_INPUT_CLASSES = 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-main-primary file:text-main-white hover:file:bg-main-primary-dark dark:file:bg-main-primary-dark dark:hover:file:bg-main-primary'
COMMON_CHECKBOX_CLASSES = 'h-4 w-4 text-main-primary border-gray-300 dark:border-gray-600 rounded focus:ring-main-primary'


# --- Formularios Existentes ---

class CarpetaForm(forms.ModelForm):
    class Meta:
        model = Carpeta
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': COMMON_TEXT_INPUT_CLASSES,
                'placeholder': 'Nombre de la nueva carpeta'
            })
        }
        labels = {
            'nombre': 'Nombre de la Carpeta'
        }

class ArchivoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Solo mostrar carpetas creadas por el usuario actual
            self.fields['carpeta'].queryset = Carpeta.objects.filter(subido_por=user).order_by('nombre')
            self.fields['carpeta'].empty_label = "Raíz (sin carpeta)" # Opcional: o "Seleccione una carpeta..."

    class Meta:
        model = Archivo
        fields = ['nombre_descriptivo', 'archivo_subido', 'carpeta']
        widgets = {
            'nombre_descriptivo': forms.TextInput(attrs={
                'class': COMMON_TEXT_INPUT_CLASSES,
                'placeholder': 'Título o descripción breve del archivo'
            }),
            'archivo_subido': forms.ClearableFileInput(attrs={
                'class': COMMON_FILE_INPUT_CLASSES
            }),
            'carpeta': forms.Select(attrs={
                'class': COMMON_SELECT_CLASSES,
            })
        }
        labels = {
            'nombre_descriptivo': 'Nombre Descriptivo',
            'archivo_subido': 'Archivo',
            'carpeta': 'Guardar en Carpeta'
        }

class ArchivoEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['carpeta'].queryset = Carpeta.objects.filter(subido_por=user).order_by('nombre')
            self.fields['carpeta'].empty_label = "Raíz (sin carpeta)"
        # Hacer el campo de archivo no obligatorio para la edición (se puede editar solo el nombre/carpeta)
        self.fields['archivo_subido'].required = False

    class Meta:
        model = Archivo
        fields = ['nombre_descriptivo', 'carpeta', 'archivo_subido'] # El orden puede ser importante
        widgets = {
            'nombre_descriptivo': forms.TextInput(attrs={
                'class': COMMON_TEXT_INPUT_CLASSES,
            }),
            'carpeta': forms.Select(attrs={
                'class': COMMON_SELECT_CLASSES,
            }),
            'archivo_subido': forms.ClearableFileInput(attrs={ # Permite limpiar el archivo actual o subir uno nuevo
                'class': COMMON_FILE_INPUT_CLASSES
            }),
        }
        labels = {
            'nombre_descriptivo': 'Nombre Descriptivo',
            'carpeta': 'Carpeta',
            'archivo_subido': 'Reemplazar Archivo (opcional)'
        }

class ArticuloWikiForm(forms.ModelForm):
    class Meta:
        model = ArticuloWiki
        fields = ['titulo', 'contenido', 'slug'] # Autor se setea en la vista
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': COMMON_TEXT_INPUT_CLASSES,
                'placeholder': 'Título del artículo'
            }),
            'contenido': forms.Textarea(attrs={
                'class': COMMON_TEXTAREA_CLASSES,
                'rows': 15,
                'placeholder': 'Escribe el contenido del artículo aquí. Se recomienda usar Markdown.'
            }),
            'slug': forms.TextInput(attrs={
                'class': COMMON_TEXT_INPUT_CLASSES,
                'placeholder': 'URL amigable (ej: como-usar-la-wiki)'
            }),
        }
        help_texts = {
            'slug': 'Dejar en blanco para autogenerar basado en el título. Usa solo letras, números, guiones o guiones bajos. Si lo modificas, asegúrate que sea único.',
            'contenido': 'Puedes usar sintaxis Markdown para dar formato al texto (encabezados, listas, negritas, etc.). Se recomienda instalar Pygments (`pip install Pygments`) para el resaltado de código.'
        }
        labels = {
            'titulo': 'Título del Artículo',
            'contenido': 'Contenido (Markdown)',
            'slug': 'Fragmento de URL (Slug)'
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            from django.utils.text import slugify as django_slugify
            if not django_slugify(slug) == slug:
                raise forms.ValidationError("El slug solo puede contener letras, números, guiones y guiones bajos.")
        return slug

# --- Nuevos Formularios ---

# 1. Formularios para el Módulo de "Formularios Dinámicos"
class FormularioModelForm(forms.ModelForm): # Para crear la metadata del formulario
    class Meta:
        model = Formulario
        fields = ['titulo', 'descripcion', 'activo', 'fecha_limite']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'placeholder': 'Título principal del formulario'}),
            'descripcion': forms.Textarea(attrs={'class': COMMON_TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Descripción o instrucciones (opcional)'}),
            'activo': forms.CheckboxInput(attrs={'class': COMMON_CHECKBOX_CLASSES + ' ml-2'}),
            'fecha_limite': forms.DateTimeInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'type': 'datetime-local'}),
        }
        labels = {
            'titulo': 'Título del Formulario',
            'descripcion': 'Descripción',
            'activo': '¿Formulario activo para recibir respuestas?',
            'fecha_limite': 'Fecha Límite para Responder (opcional)'
        }

class CampoFormularioModelForm(forms.ModelForm): # Para añadir campos a un formulario (usado en formsets)
    class Meta:
        model = CampoFormulario
        fields = ['etiqueta', 'tipo_campo', 'ayuda_texto', 'es_obligatorio', 'opciones_choices', 'orden'] # 'orden' se manejará en la vista o con JS
        widgets = {
            'etiqueta': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'placeholder': 'Pregunta o etiqueta del campo'}),
            'tipo_campo': forms.Select(attrs={'class': COMMON_SELECT_CLASSES}),
            'ayuda_texto': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'placeholder': 'Ayuda adicional (opcional)'}),
            'es_obligatorio': forms.CheckboxInput(attrs={'class': COMMON_CHECKBOX_CLASSES}),
            'opciones_choices': forms.Textarea(attrs={'class': COMMON_TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Una opción por línea (para opción múltiple, casillas, desplegable)'}),
            'orden': forms.HiddenInput(), # El orden se gestionará dinámicamente
        }
        labels = {
            'etiqueta': 'Etiqueta/Pregunta',
            'tipo_campo': 'Tipo de Campo',
            'ayuda_texto': 'Texto de Ayuda',
            'es_obligatorio': '¿Campo Obligatorio?',
            'opciones_choices': 'Opciones (si aplica)',
        }

# Nota: El formulario para *llenar* un 'Formulario' dinámico se construye en la vista o el template,
# no como una clase estática aquí, ya que sus campos dependen de las instancias de 'CampoFormulario'.

# 2. Formulario para el Módulo de Calendario
class EventoCalendarioModelForm(forms.ModelForm):
    class Meta:
        model = EventoCalendario
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin'] # Añadir 'participantes', 'color_evento' si los usas
        widgets = {
            'titulo': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'placeholder': 'Título del evento'}),
            'descripcion': forms.Textarea(attrs={'class': COMMON_TEXTAREA_CLASSES, 'rows': 4, 'placeholder': 'Descripción detallada (opcional)'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'type': 'datetime-local'}),
            # 'color_evento': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'type': 'color'}), # Si usas color_evento
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'fecha_inicio': 'Fecha y Hora de Inicio',
            'fecha_fin': 'Fecha y Hora de Fin (opcional)',
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise forms.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        return cleaned_data

# 3. Formulario para el Módulo de Tareas/Responsabilidades
class TareaModelForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'asignado_a', 'fecha_limite', 'estado', 'prioridad']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'placeholder': 'Título de la tarea'}),
            'descripcion': forms.Textarea(attrs={'class': COMMON_TEXTAREA_CLASSES, 'rows': 4, 'placeholder': 'Descripción detallada (opcional)'}),
            'asignado_a': forms.Select(attrs={'class': COMMON_SELECT_CLASSES}),
            'fecha_limite': forms.DateTimeInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'type': 'datetime-local'}),
            'estado': forms.Select(attrs={'class': COMMON_SELECT_CLASSES}),
            'prioridad': forms.Select(attrs={'class': COMMON_SELECT_CLASSES}),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'asignado_a': 'Asignar a',
            'fecha_limite': 'Fecha Límite (opcional)',
            'estado': 'Estado Actual',
            'prioridad': 'Prioridad',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar el queryset de 'asignado_a' a usuarios activos, por ejemplo
        self.fields['asignado_a'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['asignado_a'].empty_label = "Sin asignar"
        self.fields['asignado_a'].required = False # Hacer opcional la asignación directa

# 4. Formularios para Perfil de Usuario
class UserUpdateForm(forms.ModelForm): # Para campos del modelo User
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'last_name': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico Institucional',
        }

class PerfilUsuarioModelForm(forms.ModelForm): # Para campos del modelo PerfilUsuario
    class Meta:
        model = PerfilUsuario
        fields = ['departamento', 'cargo', 'telefono_extension', 'foto_perfil', 'fecha_nacimiento', 'biografia_corta']
        widgets = {
            'departamento': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'cargo': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'telefono_extension': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'foto_perfil': forms.ClearableFileInput(attrs={'class': COMMON_FILE_INPUT_CLASSES}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'type': 'date'}),
            'biografia_corta': forms.Textarea(attrs={'class': COMMON_TEXTAREA_CLASSES, 'rows': 3}),
        }
        labels = {
            'departamento': 'Departamento o Unidad',
            'cargo': 'Cargo / Puesto',
            'telefono_extension': 'Teléfono / Extensión',
            'foto_perfil': 'Foto de Perfil',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'biografia_corta': 'Sobre mí (breve)',
        }

# 5. Formularios para Reserva de Recursos
class TipoRecursoModelForm(forms.ModelForm):
    class Meta:
        model = TipoRecurso
        fields = ['nombre', 'icono_fa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'icono_fa': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'placeholder': 'ej: fas fa-projector'}),
        }

class RecursoModelForm(forms.ModelForm):
    class Meta:
        model = Recurso
        fields = ['nombre', 'tipo_recurso', 'descripcion', 'ubicacion', 'capacidad', 'esta_activo'] # 'responsable', 'requiere_aprobacion'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'tipo_recurso': forms.Select(attrs={'class': COMMON_SELECT_CLASSES}),
            'descripcion': forms.Textarea(attrs={'class': COMMON_TEXTAREA_CLASSES, 'rows': 3}),
            'ubicacion': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'capacidad': forms.NumberInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'esta_activo': forms.CheckboxInput(attrs={'class': COMMON_CHECKBOX_CLASSES + ' ml-2'}),
        }

class ReservaModelForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['recurso', 'fecha_inicio', 'fecha_fin', 'motivo'] # 'estado' se maneja en la vista
        widgets = {
            'recurso': forms.Select(attrs={'class': COMMON_SELECT_CLASSES}),
            'fecha_inicio': forms.DateTimeInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES, 'type': 'datetime-local'}),
            'motivo': forms.Textarea(attrs={'class': COMMON_TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Motivo de la reserva (opcional)'}),
        }
        labels = {
            'recurso': 'Recurso a Reservar',
            'fecha_inicio': 'Inicio de la Reserva',
            'fecha_fin': 'Fin de la Reserva',
            'motivo': 'Motivo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo recursos activos
        self.fields['recurso'].queryset = Recurso.objects.filter(esta_activo=True)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")
        recurso = cleaned_data.get("recurso")

        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                self.add_error('fecha_fin', "La fecha de fin debe ser posterior a la fecha de inicio.")
            
            if recurso:
                # Validar solapamientos (versión simplificada, puede ser más robusta)
                solapamientos = Reserva.objects.filter(
                    recurso=recurso,
                    estado=Reserva.EstadoReserva.APROBADA, # Solo contra aprobadas
                    fecha_inicio__lt=fecha_fin, # La nueva reserva no puede empezar antes de que termine una existente
                    fecha_fin__gt=fecha_inicio  # Y no puede terminar después de que empiece una existente
                )
                if self.instance and self.instance.pk: # Excluir la propia reserva si se está editando
                    solapamientos = solapamientos.exclude(pk=self.instance.pk)
                
                if solapamientos.exists():
                    self.add_error(None, f"El recurso '{recurso.nombre}' ya está reservado o se solapa con otra reserva en el horario solicitado.")
        return cleaned_data

# 6. Formularios para Gestión de Usuarios (Staff)
class UserEditStaffForm(forms.ModelForm): # Para que el staff edite usuarios
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), # ESTA ES LA LÍNEA PROBLEMÁTICA
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Grupos de Permisos"
    )
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'grupos']
        widgets = {
            'username': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'first_name': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'last_name': forms.TextInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'email': forms.EmailInput(attrs={'class': COMMON_TEXT_INPUT_CLASSES}),
            'is_active': forms.CheckboxInput(attrs={'class': COMMON_CHECKBOX_CLASSES + ' ml-2'}),
            'is_staff': forms.CheckboxInput(attrs={'class': COMMON_CHECKBOX_CLASSES + ' ml-2'}),
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
            'is_staff': 'Designa si el usuario puede iniciar sesión en el sitio de administración (Django Admin).',
            'is_active': 'Designa si este usuario debe ser tratado como activo. Desmarcar esto en lugar de borrar cuentas.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['grupos'].initial = self.instance.groups.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if hasattr(self, 'cleaned_data'): # Asegurarse de que cleaned_data existe
                user.groups.set(self.cleaned_data['grupos'])
        return user
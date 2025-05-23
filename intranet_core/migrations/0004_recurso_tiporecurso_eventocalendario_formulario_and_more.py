# Generated by Django 5.2.1 on 2025-05-15 16:05

import django.db.models.deletion
import intranet_core.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("intranet_core", "0003_articulowiki_notificacion"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Recurso",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("ubicacion", models.CharField(blank=True, max_length=150, null=True)),
                (
                    "capacidad",
                    models.PositiveIntegerField(
                        blank=True, help_text="Ej: para salas de reuniones.", null=True
                    ),
                ),
                (
                    "esta_activo",
                    models.BooleanField(
                        default=True,
                        help_text="Indica si el recurso está disponible para ser reservado.",
                    ),
                ),
            ],
            options={
                "verbose_name": "Recurso",
                "verbose_name_plural": "Recursos",
                "ordering": ["tipo_recurso", "nombre"],
            },
        ),
        migrations.CreateModel(
            name="TipoRecurso",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100, unique=True)),
                (
                    "icono_fa",
                    models.CharField(
                        blank=True,
                        help_text="Ej: 'fas fa-building', 'fas fa-desktop'",
                        max_length=50,
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Tipo de Recurso",
                "verbose_name_plural": "Tipos de Recursos",
            },
        ),
        migrations.CreateModel(
            name="EventoCalendario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("titulo", models.CharField(max_length=200)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("fecha_inicio", models.DateTimeField()),
                (
                    "fecha_fin",
                    models.DateTimeField(
                        blank=True,
                        help_text="Dejar en blanco si es un evento de día completo o sin duración específica en hora.",
                        null=True,
                    ),
                ),
                ("creado_el", models.DateTimeField(auto_now_add=True)),
                ("actualizado_el", models.DateTimeField(auto_now=True)),
                (
                    "creado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="eventos_calendario",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Evento de Calendario",
                "verbose_name_plural": "Eventos de Calendario",
                "ordering": ["fecha_inicio"],
            },
        ),
        migrations.CreateModel(
            name="Formulario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("titulo", models.CharField(max_length=255)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("creado_el", models.DateTimeField(auto_now_add=True)),
                ("activo", models.BooleanField(default=True)),
                (
                    "fecha_limite",
                    models.DateTimeField(
                        blank=True,
                        help_text="Opcional: Fecha y hora límite para enviar respuestas.",
                        null=True,
                    ),
                ),
                (
                    "creado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="formularios_creados",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Formulario",
                "verbose_name_plural": "Formularios",
                "ordering": ["-creado_el"],
            },
        ),
        migrations.CreateModel(
            name="CampoFormulario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "etiqueta",
                    models.CharField(
                        help_text="Pregunta o título del campo.", max_length=255
                    ),
                ),
                (
                    "tipo_campo",
                    models.CharField(
                        choices=[
                            ("TEXTO_CORTO", "Texto Corto"),
                            ("TEXTO_LARGO", "Texto Largo (Área de texto)"),
                            ("NUMERO", "Número"),
                            ("EMAIL", "Correo Electrónico"),
                            ("FECHA", "Fecha"),
                            ("HORA", "Hora"),
                            ("OPCION_MULTIPLE", "Opción Múltiple (una respuesta)"),
                            (
                                "CASILLAS",
                                "Casillas de Verificación (múltiples respuestas)",
                            ),
                            ("DESPLEGABLE", "Desplegable (una respuesta)"),
                            ("ARCHIVO", "Subir Archivo"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "ayuda_texto",
                    models.CharField(
                        blank=True,
                        help_text="Texto de ayuda o descripción adicional para el campo.",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("es_obligatorio", models.BooleanField(default=False)),
                (
                    "orden",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Orden en que aparecerá el campo en el formulario.",
                    ),
                ),
                (
                    "opciones_choices",
                    models.TextField(
                        blank=True,
                        help_text="Para campos de opción múltiple, casillas o desplegable. Ingrese las opciones separadas por un salto de línea (una opción por línea).",
                        null=True,
                    ),
                ),
                (
                    "formulario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="campos",
                        to="intranet_core.formulario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Campo de Formulario",
                "verbose_name_plural": "Campos de Formularios",
                "ordering": ["formulario", "orden"],
            },
        ),
        migrations.CreateModel(
            name="PerfilUsuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "departamento",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("cargo", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "telefono_extension",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "foto_perfil",
                    models.ImageField(
                        blank=True,
                        default="perfiles_usuarios/default_avatar.png",
                        null=True,
                        upload_to=intranet_core.models.user_directory_path,
                    ),
                ),
                ("fecha_nacimiento", models.DateField(blank=True, null=True)),
                (
                    "biografia_corta",
                    models.TextField(
                        blank=True,
                        help_text="Una breve descripción sobre ti.",
                        null=True,
                    ),
                ),
                (
                    "usuario",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="perfil",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Perfil de Usuario",
                "verbose_name_plural": "Perfiles de Usuarios",
            },
        ),
        migrations.CreateModel(
            name="Reserva",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fecha_inicio", models.DateTimeField()),
                ("fecha_fin", models.DateTimeField()),
                ("motivo", models.TextField(blank=True, null=True)),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("PENDIENTE", "Pendiente de Aprobación"),
                            ("APROBADA", "Aprobada"),
                            ("RECHAZADA", "Rechazada"),
                            ("CANCELADA", "Cancelada por Usuario"),
                        ],
                        default="APROBADA",
                        max_length=20,
                    ),
                ),
                ("creado_el", models.DateTimeField(auto_now_add=True)),
                (
                    "recurso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservas",
                        to="intranet_core.recurso",
                    ),
                ),
                (
                    "reservado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mis_reservas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Reserva",
                "verbose_name_plural": "Reservas",
                "ordering": ["fecha_inicio"],
            },
        ),
        migrations.CreateModel(
            name="RespuestaFormulario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("enviado_el", models.DateTimeField(auto_now_add=True)),
                (
                    "formulario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respuestas_recibidas",
                        to="intranet_core.formulario",
                    ),
                ),
                (
                    "respondido_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="respuestas_enviadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Respuesta de Formulario",
                "verbose_name_plural": "Respuestas de Formularios",
                "ordering": ["-enviado_el"],
            },
        ),
        migrations.CreateModel(
            name="DatoRespuesta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("valor", models.TextField(blank=True)),
                (
                    "campo_formulario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="intranet_core.campoformulario",
                    ),
                ),
                (
                    "respuesta_formulario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="datos",
                        to="intranet_core.respuestaformulario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Dato de Respuesta",
                "verbose_name_plural": "Datos de Respuestas",
            },
        ),
        migrations.CreateModel(
            name="Tarea",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("titulo", models.CharField(max_length=255)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_limite", models.DateTimeField(blank=True, null=True)),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("PENDIENTE", "Pendiente"),
                            ("EN_PROGRESO", "En Progreso"),
                            ("COMPLETADA", "Completada"),
                            ("CANCELADA", "Cancelada"),
                            ("EN_ESPERA", "En Espera"),
                        ],
                        default="PENDIENTE",
                        max_length=20,
                    ),
                ),
                (
                    "prioridad",
                    models.CharField(
                        choices=[
                            ("BAJA", "Baja"),
                            ("MEDIA", "Media"),
                            ("ALTA", "Alta"),
                            ("URGENTE", "Urgente"),
                        ],
                        default="MEDIA",
                        max_length=10,
                    ),
                ),
                (
                    "asignado_a",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tareas_asignadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "creado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tareas_creadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Tarea",
                "verbose_name_plural": "Tareas",
                "ordering": ["-prioridad", "fecha_limite", "fecha_creacion"],
            },
        ),
        migrations.AddField(
            model_name="recurso",
            name="tipo_recurso",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="intranet_core.tiporecurso",
            ),
        ),
    ]

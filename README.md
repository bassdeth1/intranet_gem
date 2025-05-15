# ClarityDesk Intranet

> Tu plataforma centralizada para la colaboración, gestión de información y optimización de procesos internos.

## Descripción General

ClarityDesk Intranet es una solución de intranet integral diseñada para mejorar la comunicación, la productividad y el acceso a la información dentro de la organización. Ofrece un conjunto de herramientas robustas que facilitan desde la gestión de documentos y la reserva de recursos hasta la creación de formularios dinámicos y el seguimiento de tareas.

## Características Principales

* **Gestión Documental Avanzada:**
    * Carga, organiza y comparte archivos de forma segura.
    * Estructura de carpetas personalizable (con soporte para subcarpetas).
    * Visualización en navegador para múltiples tipos de archivo.
    * Control de versiones y permisos (futurible).
* **Base de Conocimiento (Wiki):**
    * Crea y gestiona artículos utilizando Markdown.
    * Sistema de búsqueda integrado.
    * Control de autoría y fechas de actualización.
* **Notificaciones Integradas:**
    * Mantén a los usuarios informados sobre eventos importantes, tareas asignadas, etc.
    * Panel de notificaciones y sistema de "marcar como leída".
* **Formularios Dinámicos:**
    * Diseña formularios personalizados con diversos tipos de campos (texto, número, fecha, opciones múltiples, archivos, etc.).
    * Recopila y visualiza respuestas de forma organizada.
* **Calendario de Actividades y Eventos:**
    * Planifica y visualiza eventos importantes para la organización o equipos.
    * Integración visual (preparado para librerías como FullCalendar.js).
* **Gestión de Tareas y Responsabilidades:**
    * Crea, asigna y realiza seguimiento de tareas.
    * Establece prioridades, fechas límite y estados.
* **Directorio de Usuarios Interactivo:**
    * Accede a perfiles de usuario detallados.
    * Búsqueda avanzada de personal.
* **Reserva de Recursos:**
    * Gestiona y reserva recursos compartidos (salas, equipos, vehículos).
    * Visualización de disponibilidad tipo calendario.
* **Perfiles de Usuario Personalizables:**
    * Información de contacto, departamento, cargo, foto de perfil y biografía.
* **Gestión de Usuarios (Staff):**
    * Administración de cuentas de usuario, roles y permisos (para personal autorizado).
* **Interfaz Moderna y Adaptable:**
    * Diseño responsivo utilizando TailwindCSS.
    * Soporte para Modo Claro y Modo Oscuro.
* **Autenticación Segura:**
    * Inicio de sesión, cierre de sesión y cambio de contraseña.

## Tech Stack (Resumen)

* **Backend:** Django (Python)
* **Frontend:** Plantillas Django, HTML, TailwindCSS, JavaScript (vanilla)
* **Base de Datos:** SQLite3 (configurable para otras bases de datos SQL)
* **Servidor de Desarrollo:** Django Development Server

## Vista Rápida de Módulos

El proyecto se estructura principalmente en dos componentes dentro de la raíz:

* `intranet_gem/`: Este es el directorio principal del proyecto Django. Contiene:
    * `settings.py`: Configuración general del proyecto.
    * `urls.py`: Definiciones de URL a nivel de proyecto.
    * `wsgi.py` / `asgi.py`: Configuración para despliegue.
* `intranet_core/`: Esta es la aplicación principal de Django donde reside la lógica de la intranet. Incluye:
    * `models.py`: Define la estructura de la base de datos (Archivos, Tareas, Wiki, etc.).
    * `views.py`: Contiene la lógica para manejar las solicitudes y generar las respuestas.
    * `forms.py`: Define los formularios utilizados en la aplicación.
    * `urls.py`: Define las rutas específicas de la aplicación `intranet_core`.
    * `admin.py`: Configura cómo se muestran los modelos en el panel de administración de Django.
    * `templates/intranet_core/`: Plantillas HTML específicas para esta aplicación.
* `templates/`: Directorio para plantillas base y de registro (login).
* `static/`: Archivos estáticos (CSS, JavaScript, imágenes base).
* `media/`: Directorio donde se almacenarán los archivos subidos por los usuarios (configurado para no ser versionado si se sigue la guía del `.gitignore`).

## Configuración y Puesta en Marcha (Básico)

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://github.com/sindresorhus/del](https://github.com/sindresorhus/del)
    cd [Nombre del Proyecto Seleccionado]
    ```

2.  **Crear y Activar un Entorno Virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar Dependencias:**
    (Asegúrate de tener un archivo `requirements.txt`. Si no, créalo con `pip freeze > requirements.txt` después de instalar Django y otras librerías).
    ```bash
    pip install -r requirements.txt 
    # (Como mínimo: pip install django markdown django-widget-tweaks si los usas, etc.)
    # Para el resaltado de código en la Wiki, instala: pip install Pygments
    ```

4.  **Aplicar Migraciones:**
    ```bash
    python manage.py migrate
    ```

5.  **Crear un Superusuario (Administrador):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Ejecutar el Servidor de Desarrollo:**
    ```bash
    python manage.py runserver
    ```
    Accede a la intranet en `http://127.0.0.1:8000/` en tu navegador.

## Contribuciones

Actualmente, este es un proyecto en desarrollo. Si deseas contribuir:
1.  Haz un Fork del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3.  Realiza tus cambios y haz commit (`git commit -m 'Añade nueva funcionalidad X'`).
4.  Empuja tus cambios a la rama (`git push origin feature/nueva-funcionalidad`).
5.  Abre un Pull Request.

## Licencia

Este proyecto se distribuye bajo la Licencia [Nombre de la Licencia, ej: MIT] (si aplica). Reemplaza esta sección si tienes una licencia específica.

---
Desarrollado con ❤️ por [Tu Nombre/Nombre del Equipo] - 2025